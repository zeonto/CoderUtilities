# -*- coding: utf-8 -*-
# @Author: zeonto
# @Date:   2019-09-27 10:08:48
# @Last Modified by:   zeonto
# @Last Modified time: 2019-09-28 11:34:28

import sublime
import sublime_plugin
import urllib
import time
import re
from datetime import datetime
from hashlib import md5
import json
import zlib
import binascii

##
## @brief      UrlEncode 编码转码：空格转“+”号
##
class UrlEncodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = urllib.parse.quote_plus(text)
                self.view.replace(edit, region, text)


##
## @brief      UrlDecode 编码解码
##
class UrlDecodeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = urllib.parse.unquote_plus(text)
                self.view.replace(edit, region, text)


##
## @brief      获取当前 Unix 时间戳：精确到秒
##
class GetUnixTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            unix_time = int(time.time())
            self.view.insert(edit, region.begin(), str(unix_time))


##
## @brief      获取当前日期时间：格式 2016-12-22 20:25:09
##
class GetCurrentTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            ctime = time.strftime("%Y-%m-%d %H:%M:%S")
            self.view.insert(edit, region.begin(), ctime)


##
## @brief      Unix 时间戳相互转换：最小单位秒
## @todo       暂时无法识别不同格式之间转换
##
class ConvertTimeToCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                if re.match('^([0-9]+)$', text):
                    result = self.fromUnix(text)
                else:
                    result = self.toUnix(text)

                if result:
                    self.view.replace(edit, region, result)
                else:
                    sublime.error_message('不好意思哈，转换出错了(⊙o⊙)哦.')

    ##
    ## @brief      Unix 时间戳转换为日期时间
    ##
    ## @param      self       The object
    ## @param      timestamp  The timestamp
    ##
    ## @return     Y-m-d H:i:s 日期时间
    ##
    def fromUnix(self, timestamp):
        timestamp = float(timestamp)
        stamp = datetime.fromtimestamp(timestamp)
        return stamp.strftime("%Y-%m-%d %H:%M:%S")

    ##
    ## @brief      日期时间转换为 Unix 时间戳
    ##
    ## @param      self     The object
    ## @param      timestr  The timestr
    ##
    ## @return     Unix 时间戳
    ##
    def toUnix(self, timestr):
        try:
            convert_to = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
            return '%d' % (time.mktime(convert_to.timetuple()))
        except:
            return False


##
## @brief      计算 MD5 值，只限制 utf-8 编码
##
class Md5Command(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = md5(text.encode('utf-8')).hexdigest()
                self.view.replace(edit, region, text)


##
## @brief      压缩 json 格式，中文被转义则反转、排序、简化空格
##
class JsonCompressUnicodeSortCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = json.loads(text)
                line_separator = ','
                value_separator = ':'
                text = json.dumps(
                    text
                    ,ensure_ascii=False
                    ,sort_keys=True
                    ,separators=(
                        line_separator.strip(),
                        value_separator.strip()
                    )
                )
                self.view.replace(edit, region, text)


##
## @brief      展开 json 格式，中文被转义则反转、排序、简化空格
##
class JsonPerttyUnicodeSortCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                text = self.view.substr(region)
                text = json.loads(text)
                line_separator = ','
                value_separator = ':'
                text = json.dumps(
                    text
                    ,indent=4
                    ,ensure_ascii=False
                    ,sort_keys=True
                    ,separators=(
                        line_separator.strip(),
                        value_separator.strip()
                    )
                )
                self.view.replace(edit, region, text)


##
## @brief      解压 URL 请求结果
##
class UrlRequestDecompressCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            if not region.empty():
                url = self.view.substr(region)
                try:
                    text = urllib.request.urlopen(url).read()
                except urllib.error.HTTPError as e:
                    sublime.error_message("[Error - %s %s]" % (e.code, e.reason))
                    return False
                except urllib.error.URLError as e:
                    sublime.error_message("%s" % (e.reason))
                    return False
                if isinstance(text,bytes):
                    try:
                        text = zlib.decompress(text).decode('utf-8')
                    except Exception as e:
                        sublime.error_message("Invalid Response:\n--------------------------------------------------\n%s\n--------------------------------------------------" % (text.decode('utf-8')))
                        return False
                self.view.replace(edit, region, text)

