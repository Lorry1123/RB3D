# coding: utf8

from flask import Flask, Blueprint, Response, request, jsonify, session
import json
import datetime
import requests
import hashlib
from PIL import Image

from img_deal.actions import image_act as img_act


test = Blueprint('test', __name__)
DEFAULT_IMAGE_PATH = 'img_deal/img_api/img/'

from img_deal.tasks import image as img_task


@test.route('/get_pic', methods=['POST', 'GET'])
@test.route('/get_pic/<string:name>', methods=['POST', 'GET'])
def get_pic(name=''):
    img = file(DEFAULT_IMAGE_PATH + name + '.jpg')
    resp = Response(img, mimetype="image/jpeg")

    return resp


@test.route('/get_3d_pic/<string:name>', methods=['POST', 'GET'])
def get_3d_pic(name=''):
    ret = img_act.make_3d_pic(name)
    resp = Response(ret, mimetype='image/jpeg')

    return resp


@test.route('/upload_pic', methods=['POST', 'GET'])
@test.route('/upload_pic/<string:name>', methods=['POST', 'GET'])
def upload_pic(name=''):
    print 'name:', name
    file_tmp = request.files['file']
    img = Image.open(file_tmp)
    img.save(DEFAULT_IMAGE_PATH + name + '.jpg', 'jpeg')
    img_act.save_to_db(name)
    print img.size

    return jsonify(status=0, src='../img_api/get_pic/' + name, width=img.size[0], height=img.size[1])


@test.route('/get_lov', methods=['POST', 'GET'])
@test.route('/get_lov/<string:name>', methods=['POST', 'GET'])
def get_lov(name=''):
    img = file(DEFAULT_IMAGE_PATH + name + '_lov.jpg')
    resp = Response(img, mimetype='image/jpeg')

    return resp


@test.route('/make_lov', methods=['POST', 'GET'])
def make_lov():
    name = request.values.get('name')
    x_low = int(request.values.get('x_low'))
    y_low = int(request.values.get('y_low'))
    x_high = int(request.values.get('x_high'))
    y_high = int(request.values.get('y_high'))
    threshold = float(request.values.get('threshold'))
    size = int(request.values.get('size'))
    area = dict(x_low=x_low, x_high=x_high, y_low=y_low, y_high=y_high)

    ret = img_act.make_lov(name, area, threshold, size)
    resp = Response(ret, mimetype='image/jpeg')

    return resp


@test.route('/add', methods=['POST', 'GET'])
def add():
    img_task.add.delay(1, 3)

    return jsonify(status=1)


@test.route('/send_to_task', methods=['POST', 'GET'])
def send_to_task():
    print request.values.get('name'), request.values.get('x_low')
    print '-------------'
    name = request.values.get('name')
    x_low = int(request.values.get('x_low'))
    y_low = int(request.values.get('y_low'))
    x_high = int(request.values.get('x_high'))
    y_high = int(request.values.get('y_high'))
    threshold = float(request.values.get('threshold'))
    size = int(request.values.get('size'))
    screen_x = int(request.values.get('screen_x'))
    screen_y = int(request.values.get('screen_y'))
    screen_size = float(request.values.get('screen_size'))
    area = dict(x_low=x_low, x_high=x_high, y_low=y_low, y_high=y_high)
    screen = dict(width=screen_x, height=screen_y, size=screen_size)

    se = dict(uid=session['uid'], mobile=session['mobile'])

    img_task.make_3d.delay(name, area, threshold, size, screen, se)

    return jsonify(status=1)

# @test.route('/send_msg_yunpian', methods=['POST', 'GET'])
# def send_msg_yunpian():
#     phone = request.values.get('phone')
#     name = request.values.get('name')
#     obj = request.values.get('obj')
#     detail = request.values.get('detail')
#
#     print phone, name, obj, detail
#
#     url = 'https://sms.yunpian.com/v2/sms/single_send.json'
#
#     text = '【路哦汝衣网】用户sama～您在{}定制的{}已经制作完成了哦～～请登陆{}查看呢～\n以下为订单信息：{}'.format(name, obj, name, detail)
#     print text
#     data = {
#         'apikey': '44fb01a4a9f4aea703876e18606cbc5b',
#         'mobile': phone,
#         'text': text
#     }
#     resp = requests.post(url, data)
#     print 'success'
#     resp.encoding = 'utf-8'
#     ret = resp.text
#     print resp.text
#     print data
#
#     return Response(json.dumps({'msg': ret}), mimetype='application/json')
#
#
# @test.route('/send_msg_alidayu', methods=['POST', 'GET'])
# def send_msg_alidayu():
#     phone = request.values.get('phone')
#     name = request.values.get('name')
#     obj = request.values.get('obj')
#     detail = request.values.get('detail')
#     app_secret = '65c7688b51a06aa1b307d12391000f0b'
#
#     print 'json ---->', json.dumps(dict(name=name, object=obj, detail=detail))
#
#     data = dict(
#         # single send params
#         sms_param=json.dumps(dict(name=name, object=obj, detail=detail)),
#         sms_type='normal',
#         sms_free_sign_name='南理校内帮',
#         rec_num=phone,
#         sms_template_code='SMS_59100027',
#
#         # common params
#         method='alibaba.aliqin.fc.sms.num.send',
#         app_key='23725539',
#         sign_method='md5',
#         # TODO: get sign
#         timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#         format='json',
#         v='2.0'
#     )
#
#     sign = get_sign(app_secret, data)
#     print 'sign:  %s' % sign
#
#     url = 'http://gw.api.taobao.com/router/rest'
#
#     data['sign'] = sign
#     resp = requests.post(url, data)
#     print 'success'
#     resp.encoding = 'utf-8'
#     ret = resp.text
#     print resp.text
#
#     return Response(json.dumps({'msg': ret}), mimetype='application/json')
#
#
# def get_sign(secret, params):
#     keys = params.keys()
#     keys.sort()
#
#     for key in keys:
#         print key
#
#     params = "%s%s%s" % (secret,
#                          str().join('%s%s' % (key, params[key]) for key in keys),
#                          secret)
#     print params
#     sign = hashlib.md5(params).hexdigest().upper()
#
#     return sign
