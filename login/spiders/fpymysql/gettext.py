import glob
from os import path
import os
from aip import AipOcr
from PIL import Image

def convertimg(picfile, outdir):
    '''调整图片大小，对于过大的图片进行压缩
    picfile:    图片路径
    outdir：    图片输出路径
    '''
    img = Image.open(picfile)
    width, height = img.size
    while(width*height > 4000000):  # 该数值压缩后的图片大约 两百多k
        width = width // 2
        height = height // 2
    new_img=img.resize((width, height),Image.BILINEAR)
    new_img.save(path.join(outdir,os.path.basename(picfile)))
    
def baiduOCR(picfile):
    """利用百度api识别文本，并保存提取的文字
    picfile:    图片文件名
    outfile:    输出文件
    """
    filename = path.basename(picfile)
    
    APP_ID = '24360726' # 刚才获取的 ID，下同
    API_KEY = 'uUOofw6N4eXslMYcqiiBn0FV'
    SECRECT_KEY = 'MIbWYTgykYNm4fhGyd65w4E7RYganj3Y'
    client = AipOcr(APP_ID, API_KEY, SECRECT_KEY)
    
    i = open(picfile, 'rb')
    img = i.read()

    message = client.basicGeneral(img)   # 通用文字识别，每天 50 000 次免费
    #message = client.basicAccurate(img)   # 通用文字高精度识别，每天 800 次免费

    i.close();

    result = []
    for text in message.get('words_result'):
        result.append(text.get('words'))
    result = ''.join(result)
    return result



def gettext():
    outdir = 'tmp'

    if not path.exists(outdir):
        os.mkdir(outdir)

    # 首先对过大的图片进行压缩，以提高识别速度，将压缩的图片保存与临时文件夹中
    picture = 'C:\\laragon\\www\\pyenv\\login\\验证码.png'    # 删选出jpg和png格式的图片
    convertimg(picture, outdir)

    for picfile in glob.glob("tmp/*"):
        # print(picfile)
        result = baiduOCR(picfile)
        # print(result)
        os.remove(picfile)
    os.removedirs(outdir)
    return result
    
