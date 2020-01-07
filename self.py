# -*- coding: utf-8 -*-
from linepy import *
from akad.ttypes import *
from time import sleep
from gtts import gTTS
from bs4 import BeautifulSoup
from datetime import datetime
from googletrans import Translator
import ast, codecs, json, os, pytz, re, threading, random, requests, pafy, sys, time, urllib.parse, humanize

listApp = ["IOSIPAD", "CHROMEOS", "DESKTOPWIN", "DESKTOPMAC", "WIN10"]
try:
	for app in listApp:
		try:
			try:
				with open("authToken.txt", "r") as token:
					authToken = token.read()
					if not authToken:
						client = LINE()
						with open("authToken.txt","w") as token:
							token.write(client.authToken)
						continue
					client = LINE(authToken, speedThrift=False, appName="{}\t2.1.5\tPH-13\t1".format(app))
				break
			except Exception as error:
				print(error)
				if error == "REVOKE":
					exit()
				elif "auth" in error:
					continue
				else:
					exit()
		except Exception as error:
			print(error)
except Exception as error:
	print(error)
with open("authToken.txt", "w") as token:
    token.write(str(client.authToken))
clientMid = client.profile.mid
clientStart = time.time()
clientPoll = OEPoll(client)

languageOpen = codecs.open("language.json","r","utf-8")
tagmeOpen = codecs.open("tag.json","r","utf-8")
blacklistOpen = codecs.open("blacklist.json","r","utf-8")
setting2Open = codecs.open("setting2.json","r","utf-8")
readOpen = codecs.open("read.json","r","utf-8")
settingsOpen = codecs.open("setting.json","r","utf-8")
unsendOpen = codecs.open("unsend.json","r","utf-8")

language = json.load(languageOpen)
tagme = json.load(tagmeOpen)
blacklist = json.load(blacklistOpen)
setting2 = json.load(setting2Open)
read = json.load(readOpen)
settings = json.load(settingsOpen)
unsend = json.load(unsendOpen)

offbot = []
msg_dict = {}
msg_image={}
msg_video={}
msg_sticker={}
detectUnsend = []
temp_flood = {}
simisimi = []
owner = ("ud296655acef67cbd5e8208e63629f78b")
cctv = {
	"cyduk":{},
	"point":{},
	"sidermem":{}
}

def restartBot():
	print ("[ INFO ] BOT RESETTED")
	python = sys.executable
	os.execl(python, python, *sys.argv)
	
def waktu(self,secs):
	mins, secs = divmod(secs,60)
	hours, mins = divmod(mins,60)
	days, hours = divmod(hours, 24)
	return '%02d Hari %02d Jam %02d Menit %02d Detik' % (days, hours, mins, secs)

def siderMembers(to, mid):
	try:
		arrData = ""
		textx = "──────[ {} ]──────\nHaii ".format(str(len(mid)))
		arr = []
		no = 1
		num = 2
		for i in mid:
			mention = "@x\n"
			slen = str(len(textx))
			elen = str(len(textx) + len(mention) - 1)
			arrData = {'S':slen, 'E':elen, 'M':i}
			arr.append(arrData)
			textx += mention+settings["Sider"]
			if no < len(mid):
				no += 1
				textx += "%i. " % (num)
				num=(num+1)
			else:
				try:
					no = "\n╰───[ {} ]".format(str(client.getGroup(to).name))
				except:
					no = "\n╰───[ Success ]"
		client.sendMessage(to, textx, {'MENTION': str('{"MENTIONEES":' + json.dumps(arr) + '}')}, 0)
	except Exception as error:
		client.sendMessage(to, "[ INFO ] Error :\n" + str(error))

def delExpire():
    if temp_flood != {}:
        for tmp in temp_flood:
            if temp_flood[tmp]["expire"] == True:
                if time.time() - temp_flood[tmp]["time"] >= 3*10:
                    temp_flood[tmp]["expire"] = False
                    temp_flood[tmp]["time"] = time.time()
                    try:
                        userid = "https://line.me/ti/p/~" + client.profile.userid
                        client.sendFooter(tmp, "Spam is over , Now Bots Actived !", str(userid), "http://dl.profile.line-cdn.net/"+client.getContact(clientMid).pictureStatus, client.getContact(clientMid).displayName)
                    except Exception as error:
                        logError(error) 
			
def logError(text):
    client.log("[ ERROR ] {}".format(str(text)))
    tz = pytz.timezone("Asia/Makassar")
    timeNow = datetime.now(tz=tz)
    timeHours = datetime.strftime(timeNow,"(%H:%M)")
    day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
    hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    inihari = datetime.now(tz=tz)
    hr = inihari.strftime('%A')
    bln = inihari.strftime('%m')
    for i in range(len(day)):
        if hr == day[i]: hasil = hari[i]
    for k in range(0, len(bulan)):
        if bln == str(k): bln = bulan[k-1]
    time = "{}, {} - {} - {} | {}".format(str(hasil), str(inihari.strftime('%d')), str(bln), str(inihari.strftime('%Y')), str(inihari.strftime('%H:%M:%S')))
    with open("errorLog.txt","a") as error:
        error.write("\n[{}] {}".format(str(time), text))

def changeVideoAndPictureProfile(pict, vids):
    try:
        files = {'file': open(vids, 'rb')}
        obs_params = client.genOBSParams({'oid': clientMid, 'ver': '2.0', 'type': 'video', 'cat': 'vp.mp4', 'name': 'Hello_World.mp4'})
        data = {'params': obs_params}
        r_vp = client.server.postContent('{}/talk/vp/upload.nhn'.format(str(client.server.LINE_OBS_DOMAIN)), data=data, files=files)
        if r_vp.status_code != 201:
            return "Failed update profile"
        client.updateProfilePicture(pict, 'vp')
        return "Success update profile"
    except Exception as e:
        raise Exception("Error change video and picture profile %s"%str(e))
        
def changeProfileVideo(to):
    if settings['changevp']['picture'] == None:
        return client.sendReplyMessage(msg.id, to, "Foto tidak ditemukan")
    elif settings['changevp']['video'] == None:
        return client.sendReplyMessage(msg.id, to, "Video tidak ditemukan")
    else:
        path = settings['changevp']['video']
        files = {'file': open(path, 'rb')}
        obs_params = client.genOBSParams({'oid': client.getProfile().mid, 'ver': '2.0', 'type': 'video', 'cat': 'vp.mp4'})
        data = {'params': obs_params}
        r_vp = client.server.postContent('{}/talk/vp/upload.nhn'.format(str(client.server.LINE_OBS_DOMAIN)), data=data, files=files)
        if r_vp.status_code != 201:
            return client.sendReplyMessage(msg.id, to, "Gagal update profile")
        path_p = settings['changevp']['picture']
        settings['changevp']['status'] = False
        client.updateProfilePicture(path_p, 'vp')
        
def generateReplyMessage(self, relatedMessageId):
        msg = Message()
        msg.relatedMessageServiceCode = 1
        msg.messageRelationType = 3
        msg.relatedMessageId = str(relatedMessageId)
        return msg
        
def sendReplyMessage(self, relatedMessageId, to, text, contentMetadata={}, contentType=0):
        msg = self.generateReplyMessage(relatedMessageId)
        msg.to = to
        msg.text = text
        msg.contentType = contentType
        msg.contentMetadata = contentMetadata
        if to not in self._messageReq:
            self._messageReq[to] = -1
        self._messageReq[to] += 1
        return self.talk.sendMessage(self._messageReq[to], msg)
	
def timeChange(secs):
	mins, secs = divmod(secs,60)
	hours, mins = divmod(mins,60)
	days, hours = divmod(hours,24)
	weeks, days = divmod(days,7)
	months, weeks = divmod(weeks,4)
	text = ""
	if months != 0: text += "%02d Bulan" % (months)
	if weeks != 0: text += " %02d Minggu" % (weeks)
	if days != 0: text += " %02d Hari" % (days)
	if hours !=  0: text +=  " %02d Jam" % (hours)
	if mins != 0: text += " %02d Menit" % (mins)
	if secs != 0: text += " %02d Detik" % (secs)
	if text[0] == " ":
		text = text[1:]
	return text

def command(text):
	pesan = text.lower()
	if settings["setKey"] == True:
		if pesan.startswith(settings["keyCommand"]):
			cmd = pesan.replace(settings["keyCommand"],"")
		else:
			cmd = "Undefined command"
	else:
		cmd = text.lower()
	return cmd

def backupData():
	try:
		backup = read
		f = codecs.open('read.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		backup = tagme
		f = codecs.open('tag.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		backup = settings
		f = codecs.open('setting.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		backup = unsend
		f = codecs.open('unsend.json','w','utf-8')
		json.dump(backup, f, sort_keys=True, indent=4, ensure_ascii=False)
		return True
	except Exception as error:
		logError(error)
		return False

def clientBot(op):
	try:
		if op.type == 0:
			return

		if op.type == 5:
			print ("[ 5 ] NOTIFIED ADD CONTACT")
			if settings["autoAdd"] == True:
				client.findAndAddContactsByMid(op.param1)
			client.sendMention(op.param1, settings["autoAddMessage"], [op.param1])

		if op.type == 13:
			print ("[ 13 ] NOTIFIED INVITE INTO GROUP")
			if settings["autoJoin"] and clientMid in op.param3:
				client.acceptGroupInvitation(op.param1)
				
		if op.type == 25:
			try:
				msg = op.message
				text = str(msg.text)
				msg_id = msg.id
				receiver = msg.to
				sender = msg._from
				cmd = command(text)
				print("[ 25 ] COMMAND [{}]".format(str(cmd)))
				setKey = settings["keyCommand"].title()
				if settings["setKey"] == False:
					setKey = ''
				if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
					if msg.toType == 0:
						if sender != client.profile.mid:
							to = sender
						else:
							to = receiver
					elif msg.toType == 1:
						to = receiver
					elif msg.toType == 2:
						to = receiver
					if msg.contentType == 0:
						if cmd == "mute":
								if to not in offbot:
									client.sendReplyMessage(msg.id, to, "「RUNTIME」\nBerhasil mengaktifkan mute di group \n{}".format(client.getGroup(to).name))
									offbot.append(to)
									print (to)
								else:
									client.sendReplyMessage(msg.id, to, "「RUNTIME」\nMute di group {} telah on".format(client.getGroup(to).name))
						elif cmd == "unmute":
								if to in offbot:
									offbot.remove(to)
									client.sendReplyMessage(msg.id, to, "「RUNTIME」\nBerhasil mematikan mute di group \n{}".format(client.getGroup(to).name))
									print (to)
								else:
									client.sendReplyMessage(msg.id, to, "「RUNTIME」\nUnmute di group {} telah mati".format(client.getGroup(to).name))
						if to in offbot:
							return
						elif cmd == "logout":
							client.sendReplyMessage(msg.id, to, "「LOGOUT」\nBerhasil mematikan selfbot")
							sys.exit("[ INFO ] BOT SHUTDOWN")
							return
						elif cmd == "restart":
							client.sendReplyMessage(msg.id, to, "「RESTART」\nBerhasil mereset bot")
							restartBot()
						elif cmd == "speed":
							start = time.time()
							client.sendReplyMessage(msg.id, to, "Menghitung kecepatan...")
							elapsed_time = time.time() - start
							client.sendReplyMessage(msg.id, to, "Kecepatan mengirim pesan {} detik".format(str(elapsed_time)))
						elif cmd == "runtime":
							timeNow = time.time()
							runtime = timeNow - clientStart
							runtime = timeChange(runtime)
							client.sendReplyMessage(msg.id, to, "「RUNTIME」\ntelah aktif selama {}".format(str(runtime)))
						elif cmd.startswith("setkey: "):
							sep = text.split(" ")
							key = text.replace(sep[0] + " ","")
							if " " in key:
								client.sendReplyMessage(msg.id, to, "Key tidak bisa menggunakan spasi")
							else:
								settings["keyCommand"] = str(key).lower()
								client.sendReplyMessage(msg.id, to, "「SET KEY」\nBerhasil mengubah set key command menjadi : 「{}」".format(str(key).lower()))
						elif cmd.startswith("setfotterlink: "):
							sep = text.split(" ")
							key = text.replace(sep[0] + " ","")
							if " " in key:
								client.sendReplyMessage(msg.id, to, "Key tidak bisa menggunakan spasi")
							else:
								settings["fotterlink"] = str(key).lower()
								client.sendReplyMessage(msg.id, to, "「SET FOTTER LINK」\nBerhasil mengubah link fotter menjadi :\n「{}」".format(str(key).lower()))
						elif cmd == "help1":
							helpMessage = menuHelp()
							client.sendReplyMessage(msg.id, to, helpMessage)
						elif cmd == "help2":
							helpTextToSpeech = menuMy()
							client.sendReplyMessage(msg.id, to, helpTextToSpeech)
						elif cmd == "help3":
							helpTranslate = menuGet()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "help4":
							helpTranslate = menuGroup()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "help5":
							helpTranslate = menuMimic()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "help6":
							helpTranslate = menuChange()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "help7":
							helpTranslate = menuSpam()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "help":
							helpTranslate = menuHelp1()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "favorite":
							helpTranslate = menuFav()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "settings":
							helpTranslate = menuStatus()
							client.sendReplyMessage(msg.id, to, helpTranslate)
						elif cmd == "dell":
							client.removeAllMessages(op.param2)
							client.sendMessage(to, "Cleaning all chat success")
						elif cmd.startswith("unsend "):
							sep = text.split(" ")
							args = text.replace(sep[0] + " ","")
							mes = int(sep[1])
							try:
								mes = int(args[1])
							except:
								mes = 1
							M = client.getRecentMessagesV2(to, 1001)
							MId = []
							for ind,i in enumerate(M):
								if ind == 0:
									pass
								else:
									if i._from == client.profile.mid:
										MId.append(i.id)
										if len(MId) == mes:
											break
							def unsMes(id):
								client.unsendMessage(id)
							for i in MId:
								thread1 = threading.Thread(target=unsMes, args=(i,))
								thread1.daemon = True
								thread1.start()
								thread1.join()
							client.sendReplyMessage(msg.id, to, "「UNSEND」\nSuccess unsend {} message.".format(len(MId)))
						elif cmd == "detectunsend on":
								if to in detectUnsend:
									client.sendReplyMessage(msg.id, to, "「DETECT UNSEND」\nDetect unsend telah aktif di group {}".format(client.getGroup(to).name))
								else:
									detectUnsend.append(to)
									client.sendReplyMessage(msg.id, to, "「DETECT UNSEND」\nBerhasil mengaktifkan detect unsend di group {}".format(client.getGroup(to).name))
						elif cmd == "detectunsend off":
								if to in detectUnsend:
									detectUnsend.remove(to)
									client.sendReplyMessage(msg.id, to, "「DETECT UNSEND」\nBerhasil menonaktifkan detect unsend di group {}".format(client.getGroup(to).name))
								else:
									client.sendReplyMessage(msg.id, to, "「DETECT UNSEND」\nDetect unsend telah nonaktif di group {}".format(client.getGroup(to).name))
						elif cmd == "delmentionme":
								del tagme['ROM'][to]
								client.sendReplyMessage(msg.id, to, "「DEL MENTIONME」\nBerhasil menghapus data Mention di group \n{}".format(client.getGroup(to).name))
						elif cmd == "mentionme":
								if to in tagme['ROM']:
									moneys = {}
									msgas = ''
									for a in tagme['ROM'][to].items():
										moneys[a[0]] = [a[1]['msg.id'],a[1]['waktu']] if a[1] is not None else idnya
									sort = sorted(moneys)
									sort.reverse()
									sort = sort[0:]
									msgas = '[Mention Me]'
									h = []
									no = 0
									for m in sort:
										has = ''
										nol = -1
										for kucing in moneys[m][0]:
											nol+=1
											has+= '\nline://nv/chatMsg?chatId={}&messageId={} \n{}'.format(to,kucing,humanize.naturaltime(datetime.fromtimestamp(moneys[m][1][nol]/1000)))
										h.append(m)
										no+=1
										if m == sort[0]:
											msgas+= '\n{}. @!{}x{}'.format(no,len(moneys[m][0]),has)
										else:
											msgas+= '\n\n{}. @!{}x{}'.format(no,len(moneys[m][0]),has)
									client.sendMention(to, msgas, h)
								else:
									msgas = 'Sorry @!In {} nothink get a mention'.format(client.getGroup(to).name)
									client.sendMention(to, msgas, [sender])
						elif cmd == 'mentionall':
							group = client.getGroup(to)
							midMembers = [contact.mid for contact in group.members]
							midSelect = len(midMembers)//20
							for mentionMembers in range(midSelect+1):
								no = 0
								ret_ = "╭───「 Mention 」"
								dataMid = []
								for dataMention in group.members[mentionMembers*20 : (mentionMembers+1)*20]:
									dataMid.append(dataMention.mid)
									no += 1
									ret_ += "\n├ {}. @!".format(str(no))
								ret_ += "\n╰───「{} Member」".format(str(len(dataMid)))
								client.sendMention(to, ret_, dataMid)
						elif cmd == "about":
								groups = client.getGroupIdsJoined()
								contacts = client.getAllContactIds()
								blockeds = client.getBlockedContactIds()
								tz = pytz.timezone("Asia/Jakarta")
								lists = []
								timeNow = datetime.now(tz=tz)
								day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
								hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
								bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
								hr = timeNow.strftime("%A")
								bln = timeNow.strftime("%m")
								timeNoww = time.time()
								runtime = timeNoww - clientStart
								runtime = timeChange(runtime)
								for i in range(len(day)):
									if hr == day[i]: hasil = hari[i]
								for k in range(0, len(bulan)):
									if bln == str(k): bln = bulan[k-1]
								readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\n│ Jam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
								name = "「SELFBOT」"
								result = "╭───「About」"
								result += "\n│ Name : {}".format(client.getProfile().displayName)
								result += "\n│ Version : Premium"
								result += "\n│ Selfbot : Active"
								result += "\n│ Group : {}".format(str(len(groups)))
								result += "\n│ Friend : {}".format(str(len(contacts)))
								result += "\n│ Blocked : {}".format(str(len(blockeds)))
								result += "\n├───────────"
								result += "\n│ {}".format(readTime)
								result += "\n├───────────"
								result += "\n│ Bot Runtime :"
								result += "\n│ {}".format(str(runtime))
								result += "\n╰───────────"
								client.sendReplyMessage(msg.id, to, result)
						elif cmd.startswith ('spamcall '):
								if msg.toType == 2:
									sep = text.split(" ")
									strnum = text.replace(sep[0] + " ","")
									num = int(strnum)
									client.sendReplyMessage(msg.id, to, "「SPAM CALL」\nBerhasil mengundangan Free Call group")
									for var in range(0,num):
										group = client.getGroup(to)
										members = [mem.mid for mem in group.members]
										client.acquireGroupCallRoute(to)
										client.inviteIntoGroupCall(to, contactIds=members)
						elif cmd.startswith("spamcallto"):
								dan = text.split(" ")
								num = int(dan[1])
								ret_ = "╭───「 Spam 」"
								if 'MENTION' in msg.contentMetadata.keys()!= None:
									names = re.findall(r'@(\w+)', text)
									mention = ast.literal_eval(msg.contentMetadata['MENTION'])
									mentionees = mention['MENTIONEES']
									lists = []
									for mention in mentionees:
										if mention["M"] not in lists:
											lists.append(mention["M"])
									for ls in lists:
										for var in range(0,num):
											group = client.getGroup(to)
											members = [ls]
											client.acquireGroupCallRoute(to)
											client.inviteIntoGroupCall(to, contactIds=members)
										ret_ += "\n├ @!"
									ret_ += "\n╰───────────".format(str(dan[1]))
									client.sendMention(to, ret_, lists)
						elif cmd.startswith("spamtag"):
								dan = text.split(" ")
								num = int(dan[1])
								text = "「SPAM MENTION」\nBerhasil {} spam mention".format(str(dan[1]))
								if 'MENTION' in msg.contentMetadata.keys()!= None:
									names = re.findall(r'@(\w+)', text)
									mention = ast.literal_eval(msg.contentMetadata['MENTION'])
									mentionees = mention['MENTIONEES']
									lists = []
									for mention in mentionees:
										if mention["M"] not in lists:
											lists.append(mention["M"])
									for ls in lists:
										for var in range(0,num):
											client.sendMention(to, "@!", [ls])
									client.sendReplyMessage(msg.id, to, text)
						elif cmd.startswith("spamtext"):
								text = text.split(" ")
								jmlh = int(text[2])
								balon = jmlh * (text[3]+"\n")
								if text[1] == "on":
									if jmlh <= 50:
										for x in range(jmlh):
											client.sendReplyMessage(msg.id, to, text[3])
									else:
										client.sendMention(to, "@! Maaf jumlah terlalu banyak", [sender])
								elif text[1] == "off":
									if jmlh <= 50:
										client.sendReplyMessage(msg.id, to, balon)
									else:
										client.sendMention(to, "@! Maaf jumlah terlalu banyak", [sender])
						elif cmd.startswith("cancelall"):
								if msg.toType == 2:
									group = client.getGroup(to)
									if group.invitee is None or group.invitee == []:
										client.sendReplyMessage(msg.id, to, "Tidak ada pendingan")
									else:
										invitee = [contact.mid for contact in group.invitee]
										for inv in invitee:
											client.cancelGroupInvitation(to, [inv])
										client.sendReplyMessage(msg.id, to, "「CANCELALL」\nBerhasil membersihkan {} pendingan".format(str(len(invitee))))
						elif cmd == "status":
							try:
								ret_ = "╭───「 Status 」"
								if settings["autoAdd"] == True: ret_ += "\n├ Auto Add : ON"
								else: ret_ += "\n├ Auto Add : OFF"
								if settings["autoJoin"] == True: ret_ += "\n├ Auto Join : ON"
								else: ret_ += "\n├ Auto Join : OFF"
								if settings["autoJoinTicket"] == True: ret_ += "\n├ Auto Join Ticket : ON"
								else: ret_ += "\n├ Auto Join Ticket : OFF"
								if settings["autoRead"] == True: ret_ += "\n├ Auto Read : ON"
								else: ret_ += "\n├ Auto Read : OFF"
								if settings["autoRespon"] == True: ret_ += "\n├ Auto Respon : ON"
								else: ret_ += "\n├ Auto Respon : OFF"
								if settings["checkContact"] == True: ret_ += "\n├ Check Contact : ON"
								else: ret_ += "\n├ Check Contact : OFF"
								if settings["checkPost"] == True: ret_ += "\n├ Check Post : ON"
								else: ret_ += "\n├ Check Post : OFF"
								if settings["checkSticker"] == True: ret_ += "\n├ Check Sticker : ON"
								else: ret_ += "\n├ Check Sticker : OFF"
								if settings["detectUnsend"] == True: ret_ += "\n├ Detect Unsend : ON"
								else: ret_ += "\n├ Detect Unsend : OFF"
								if settings["setKey"] == True: ret_ += "\n├ Set Key : ON"
								else: ret_ += "\n├ Set Key : OFF"
								ret_ +="\n├ Auto Add Message : {}".format(settings["autoAddMessage"])
								ret_ +="\n├ Auto Join Message : {}".format(settings["autoJoinMessage"])
								ret_ +="\n├ Auto Respon Message : {}".format(settings["autoResponMessage"])
								ret_ += "\n╰───────────"
								client.sendReplyMessage(msg.id, to, str(ret_))
							except Exception as error:
								logError(error)
						elif cmd == "autoadd on":
							if settings["autoAdd"] == True:
								client.sendReplyMessage(msg.id, to, "「AUTO ADD」\nAuto add telah aktif")
							else:
								settings["autoAdd"] = True
								client.sendReplyMessage(msg.id, to, "「AUTO ADD」\nBerhasil mengaktifkan auto add")
						elif cmd == "autoadd off":
							if settings["autoAdd"] == False:
								client.sendReplyMessage(msg.id, to, "「AUTO ADD」\nAuto add telah nonaktif")
							else:
								settings["autoAdd"] = False
								client.sendReplyMessage(msg.id, to, "「AUTO ADD」\nBerhasil menonaktifkan auto add")
						elif cmd == "autojoin on":
							if settings["autoJoin"] == True:
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN」\nAuto join telah aktif")
							else:
								settings["autoJoin"] = True
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN」\nBerhasil mengaktifkan auto join")
						elif cmd == "autojoin off":
							if settings["autoJoin"] == False:
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN」\nAuto join telah nonaktif")
							else:
								settings["autoJoin"] = False
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN」\nBerhasil menonaktifkan auto join")
						elif cmd == "autojoinlink on":
							if settings["autoJoinTicket"] == True:
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN LINK」\nAuto join ticket telah aktif")
							else:
								settings["autoJoinTicket"] = True
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN LINK」\nBerhasil mengaktifkan auto join ticket")
						elif cmd == "autojoinlink off":
							if settings["autoJoinTicket"] == False:
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN LINK」\nAuto join ticket telah nonaktif")
							else:
								settings["autoJoinTicket"] = False
								client.sendReplyMessage(msg.id, to, "「AUTO JOIN LINK」\nBerhasil menonaktifkan auto join ticket")
						elif cmd == "autoread on":
							if settings["autoRead"] == True:
								client.sendReplyMessage(msg.id, to, "「AUTO READ」\nAuto read telah aktif")
							else:
								settings["autoRead"] = True
								client.sendReplyMessage(msg.id, to, "「AUTO READ」\nBerhasil mengaktifkan auto read")
						elif cmd == "autoread off":
							if settings["autoRead"] == False:
								client.sendReplyMessage(msg.id, to, "「AUTO READ」\nAuto read telah nonaktif")
							else:
								settings["autoRead"] = False
								client.sendReplyMessage(msg.id, to, "「AUTO READ」\nBerhasil menonaktifkan auto read")
						elif cmd == "autorespon on":
							if settings["autoRespon"] == True:
								client.sendReplyMessage(msg.id, to, "「AUTO RESPON」\nAuto respon telah aktif")
							else:
								settings["autoRespon"] = True
								client.sendReplyMessage(msg.id, to, "「AUTO RESPON」\nBerhasil mengaktifkan auto respon")
						elif cmd == "autorespon off":
							if settings["autoRespon"] == False:
								client.sendReplyMessage(msg.id, to, "「AUTO RESPON」\nAuto respon telah nonaktif")
							else:
								settings["autoRespon"] = False
								client.sendReplyMessage(msg.id, to, "「AUTO RESPON」\nBerhasil menonaktifkan auto respon")
						elif cmd == "checkcontact on":
							if settings["checkContact"] == True:
								client.sendReplyMessage(msg.id, to, "「CHECK CONTACT」\nCheck details contact telah aktif")
							else:
								settings["checkContact"] = True
								client.sendReplyMessage(msg.id, to, "「CHECK CONTACT」\nBerhasil mengaktifkan check details contact")
						elif cmd == "checkcontact off":
							if settings["checkContact"] == False:
								client.sendReplyMessage(msg.id, to, "「CHECK CONTACT」\nCheck details contact telah nonaktif")
							else:
								settings["checkContact"] = False
								client.sendReplyMessage(msg.id, to, "「CHECK CONTACT」\nBerhasil menonaktifkan Check details contact")
						elif cmd == "checkpost on":
							if settings["checkPost"] == True:
								client.sendReplyMessage(msg.id, to, "「CHECK POST」\nCheck details post telah aktif")
							else:
								settings["checkPost"] = True
								client.sendReplyMessage(msg.id, to, "「CHECK POST」\nBerhasil mengaktifkan check details post")
						elif cmd == "checkpost off":
							if settings["checkPost"] == False:
								client.sendReplyMessage(msg.id, to, "「CHECK POST」\nCheck details post telah nonaktif")
							else:
								settings["checkPost"] = False
								client.sendReplyMessage(msg.id, to, "「CHECK POST」\nBerhasil menonaktifkan check details post")
						elif cmd == "checksticker on":
							if settings["checkSticker"] == True:
								client.sendReplyMessage(msg.id, to, "「CHECK STIKER」\nCheck details sticker telah aktif")
							else:
								settings["checkSticker"] = True
								client.sendReplyMessage(msg.id, to, "「CHECK STIKER」\nBerhasil mengaktifkan check details sticker")
						elif cmd == "checksticker off":
							if settings["checkSticker"] == False:
								client.sendReplyMessage(msg.id, to, "「CHECK STIKER」\nCheck details sticker telah nonaktif")
							else:
								settings["checkSticker"] = False
								client.sendReplyMessage(msg.id, to, "「CHECK STIKER」\nBerhasil menonaktifkan check details sticker")
						elif cmd == "detectunsend on":
							if settings["detectUnsend"] == True:
								client.sendReplyMessage(msg.id, to, "Detect unsend telah aktif")
							else:
								settings["detectUnsend"] = True
								client.sendReplyMessage(msg.id, to, "Berhasil mengaktifkan detect unsend")
						elif cmd == "detectunsend off":
							if settings["detectUnsend"] == False:
								client.sendReplyMessage(msg.id, to, "Detect unsend telah nonaktif")
							else:
								settings["detectUnsend"] = False
								client.sendReplyMessage(msg.id, to, "Berhasil menonaktifkan detect unsend")
						elif cmd.startswith("setautoaddmessage: "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							try:
								settings["autoAddMessage"] = txt
								client.sendReplyMessage(msg.id, to, "「SET AUTO ADD」\nBerhasil mengubah pesan auto add menjadi : 「{}」".format(txt))
							except:
								client.sendReplyMessage(msg.id, to, "「SET AUTO ADD」\nGagal mengubah pesan auto add")
						elif cmd.startswith("setautoresponmessage: "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							try:
								settings["autoResponMessage"] = txt
								client.sendReplyMessage(msg.id, to, "「SET AUTO RESPON」\nBerhasil mengubah pesan auto respon menjadi : 「{}」".format(txt))
							except:
								client.sendReplyMessage(msg.id, to, "「SET AUTO RESPON」\nGagal mengubah pesan auto respon")
						elif cmd.startswith("setautojoinmessage: "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							try:
								settings["autoJoinMessage"] = txt
								client.sendReplyMessage(msg.id, to, "「SET AUTO JOIN」\nBerhasil mengubah pesan auto join menjadi : 「{}」".format(txt))
							except:
								client.sendReplyMessage(msg.id, to, "「SET AUTO JOIN」\nGagal mengubah pesan auto join")
						
						elif cmd.startswith("changename: "):
							sep = text.split(" ")
							name = text.replace(sep[0] + " ","")
							if len(name) <= 20:
								profile = client.getProfile()
								profile.displayName = name
								client.updateProfile(profile)
								client.sendReplyMessage(msg.id, to, "「CHANGE NAME」\nBerhasil mengubah nama menjadi : {}".format(name))
						elif cmd.startswith("changebio: "):
							sep = text.split(" ")
							bio = text.replace(sep[0] + " ","")
							if len(bio) <= 500:
								profile = client.getProfile()
								profile.statusMessage = bio
								client.updateProfile(profile)
								client.sendReplyMessage(msg.id, to, "「CHANGE BIO」\nBerhasil mengubah bio menjadi : {}".format(bio))
						elif cmd == "me":
							client.sendMention(to, "「ME」\n@!", [sender])
							client.sendContact(to, sender)
						elif cmd == "myprofile":
							contact = client.getContact(sender)
							cover = client.getProfileCoverURL(sender)
							result = "╭───「 Profile 」"
							result += "\n├ Display Name : @!"
							result += "\n├ Mid : {}".format(contact.mid)
							result += "\n├ Status Message : {}".format(contact.statusMessage)
							result += "\n├ Picture Profile : http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus)
							result += "\n├ Cover : {}".format(str(cover))
							result += "\n╰───────────"
							client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
							client.sendMention(to, result, [sender])
						elif cmd == "mymid":
							contact = client.getContact(sender)
							client.sendMention(to, "「MY MID」\n@!: {}".format(contact.mid), [sender])
						elif cmd == "myname":
							contact = client.getContact(sender)
							client.sendMention(to, "「MY NAME」\n@!: {}".format(contact.displayName), [sender])
						elif cmd == "mybio":
							contact = client.getContact(sender)
							client.sendMention(to, "「MY BIO」\n@!:\n{}".format(contact.statusMessage), [sender])
						elif cmd == "mypicture":
							contact = client.getContact(sender)
							client.sendReplyMessage(msg.id, to, "「MY PICTURE PROFILE」")
							client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
						elif cmd == "myvideo":
							contact = client.getContact(sender)
							if contact.videoProfile == None:
								return client.sendReplyMessage(msg.id, to, "Anda tidak memiliki video profile")
							client.sendReplyMessage(msg.id, to, "「MY VIDEO PROFILE」")
							client.sendVideoWithURL(to, "http://dl.profile.line-cdn.net/{}/vp".format(contact.pictureStatus))
						elif cmd == "mycover":
							cover = client.getProfileCoverURL(sender)
							client.sendReplyMessage(msg.id, to, "「MY COVER PROFILE」")
							client.sendImageWithURL(to, str(cover))
						elif cmd.startswith("getmid "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									client.sendMention(to, "「MID TARGET」\n@!: {}".format(ls), [ls])
						elif cmd.startswith("getname "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									contact = client.getContact(ls)
									client.sendMention(to, "「NAME TARGET」\n@!: {}".format(contact.displayName), [ls])
						elif cmd.startswith("getbio "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									contact = client.getContact(ls)
									client.sendMention(to, "「BIO TARGET」\n@!:\n{}".format(contact.statusMessage), [ls])
						elif cmd.startswith("getpicture "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									contact = client.getContact(ls)
									client.sendReplyMessage(msg.id, to, "「PICTURE PROFILE TARGET」")
									client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
						elif cmd.startswith("getvideoprofile "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									contact = client.getContact(ls)
									if contact.videoProfile == None:
										return client.sendMention(to, "@!tidak memiliki video profile", [ls])
									client.sendReplyMessage(msg.id, to, "「VIDEO PROFILE TARGET」")
									client.sendVideoWithURL(to, "http://dl.profile.line-cdn.net/{}/vp".format(contact.pictureStatus))
						elif cmd.startswith("getcover "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									cover = client.getProfileCoverURL(ls)
									client.sendReplyMessage(msg.id, to, "「COVER PROFILE TARGET」")
									client.sendImageWithURL(to, str(cover))
						elif cmd.startswith("cloneprofile "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									client.cloneContactProfile(ls)
									client.sendContact(to, sender)
									client.sendReplyMessage(msg.id, to, "「CLONE PROFILE」\nBerhasil clone profile")
						elif cmd == "restoreprofile":
							try:
								clientProfile = client.getProfile()
								clientProfile.displayName = str(settings["myProfile"]["displayName"])
								clientProfile.statusMessage = str(settings["myProfile"]["statusMessage"])
								clientPictureStatus = client.downloadFileURL("http://dl.profile.line-cdn.net/{}".format(str(settings["myProfile"]["pictureStatus"])), saveAs="LineAPI/tmp/backupPicture.bin")
								coverId = str(settings["myProfile"]["coverId"])
								client.updateProfile(clientProfile)
								client.updateProfileCoverById(coverId)
								client.updateProfilePicture(clientPictureStatus)
								client.sendReplyMessage(msg.id, to, "「RESTORE PROFILE」\nBerhasil restore profile")
								client.sendContact(to, sender)
								client.deleteFile(clientPictureStatus)
							except Exception as error:
								logError(error)
								client.sendReplyMessage(msg.id, to, "「RESTORE PROFILE」\nGagal restore profile")
						elif cmd == "backupprofile":
							try:
								clientProfile = client.getProfile()
								settings["myProfile"]["displayName"] = str(clientProfile.displayName)
								settings["myProfile"]["statusMessage"] = str(clientProfile.statusMessage)
								settings["myProfile"]["pictureStatus"] = str(clientProfile.pictureStatus)
								coverId = client.getProfileDetail()["result"]["objectId"]
								settings["myProfile"]["coverId"] = str(coverId)
								client.sendReplyMessage(msg.id, to, "「BACKUP PROFILE」\nBerhasil backup profile")
							except Exception as error:
								logError(error)
								client.sendReplyMessage(msg.id, to, "「BACKUP PROFILE」\nGagal backup profile")
						elif cmd == "friendlist":
							contacts = client.getAllContactIds()
							num = 0
							result = "╭───「 Friendlist 」"
							for listContact in contacts:
								contact = client.getContact(listContact)
								num += 1
								result += "\n├ {}. {}".format(num, contact.displayName)
							result += "\n╰───「 {} Friends 」".format(len(contacts))
							client.sendReplyMessage(msg.id, to, result)
						elif cmd.startswith("friendinfo "):
							sep = text.split(" ")
							query = text.replace(sep[0] + " ","")
							contacts = client.getAllContactIds()
							try:
								listContact = contacts[int(query)-1]
								contact = client.getContact(listContact)
								cover = client.getProfileCoverURL(listContact)
								result = "╭───「 Details Friends 」"
								result += "\n├ Display Name : @!"
								result += "\n├ Mid : {}".format(contact.mid)
								result += "\n├ Status Message : {}".format(contact.statusMessage)
								result += "\n├ Picture Profile : http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus)
								result += "\n├ Cover : {}".format(str(cover))
								result += "\n╰───────────"
								client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(contact.pictureStatus))
								client.sendMention(to, result, [contact.mid])
							except Exception as error:
								logError(error)
						elif cmd == "blocklist":
							blockeds = client.getBlockedContactIds()
							num = 0
							result = "╭───「 Blocked 」"
							for listBlocked in blockeds:
								contact = client.getContact(listBlocked)
								num += 1
								result += "\n├ {}. {}".format(num, contact.displayName)
							result += "\n╰──「 {} Blocked 」".format(len(blockeds))
							client.sendReplyMessage(msg.id, to, result)
						elif cmd.startswith("friendbroadcast: "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							contacts = client.getAllContactIds()
							for contact in contacts:
								client.sendMessage(contact, "[ Broadcast ]\n{}".format(str(txt)))
							client.sendReplyMessage(msg.id, to, "「FRIEND BROADCAST」\nBerhasil broadcast ke {} teman".format(str(len(contacts))))
						elif cmd.startswith("groupname: "):
							if msg.toType == 2:
								sep = text.split(" ")
								groupname = text.replace(sep[0] + " ","")
								if len(groupname) <= 20:
									group = client.getGroup(to)
									group.name = groupname
									client.updateGroup(group)
									client.sendReplyMessage(msg.id, to, "「CHANGE GROUP NAME」\nBerhasil mengubah nama group menjadi : {}".format(groupname))
						elif cmd == "openqr":
							if msg.toType == 2:
								group = client.getGroup(to)
								group.preventedJoinByTicket = False
								client.updateGroup(group)
								groupUrl = client.reissueGroupTicket(to)
								client.sendReplyMessage(msg.id, to, "「OPEN LINK/QR GROUP」\nBerhasil membuka QR Group\n\nGroupURL : line://ti/g/{}".format(groupUrl))
						elif cmd == "closeqr":
							if msg.toType == 2:
								group = client.getGroup(to)
								group.preventedJoinByTicket = True
								client.updateGroup(group)
								client.sendReplyMessage(msg.id, to, "「CLOSE LINK/QR GROUP」\nBerhasil menutup QR Group")
						elif cmd == "grouppicture":
							if msg.toType == 2:
								group = client.getGroup(to)
								groupPicture = "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus)
								client.sendImageWithURL(to, groupPicture)
						elif cmd == "groupname":
							if msg.toType == 2:
								group = client.getGroup(to)
								client.sendReplyMessage(msg.id, to, "「GROUP NAME」\nNama Group : {}".format(group.name))
						elif cmd == "groupid":
							if msg.toType == 2:
								group = client.getGroup(to)
								client.sendReplyMessage(msg.id, to, "「GROUP ID」\nGroup ID : {}".format(group.id))
						elif cmd == "grouplist":
							groups = client.getGroupIdsJoined()
							ret_ = "╭───「 Grouplist 」"
							no = 0
							for gid in groups:
								group = client.getGroup(gid)
								no += 1
								ret_ += "\n├ {}. {} | {}".format(str(no), str(group.name), str(len(group.members)))
							ret_ += "\n╰───「 {} Groups 」".format(str(len(groups)))
							client.sendReplyMessage(msg.id, to, str(ret_))
						elif cmd == "memberlist":
							if msg.toType == 2:
								group = client.getGroup(to)
								num = 0
								ret_ = "╭───「 Memberlist 」"
								for contact in group.members:
									num += 1
									ret_ += "\n├ {}. {}".format(num, contact.displayName)
								ret_ += "\n╰───「 {} Members 」".format(len(group.members))
								client.sendReplyMessage(msg.id, to, ret_)
						elif cmd == "pendinglist":
							if msg.toType == 2:
								group = client.getGroup(to)
								ret_ = "╭───「 Pendinglist 」"
								no = 0
								if group.invitee is None or group.invitee == []:
									return client.sendReplyMessage(msg.id, to, "Tidak ada pendingan")
								else:
									for pending in group.invitee:
										no += 1
										ret_ += "\n├ {}. {}".format(str(no), str(pending.displayName))
									ret_ += "\n╰───「 {} Pendings 」".format(str(len(group.invitee)))
									client.sendReplyMessage(msg.id, to, str(ret_))
						elif cmd == "groupinfo":
							group = client.getGroup(to)
							try:
								try:
									groupCreator = group.creator.mid
								except:
									groupCreator = "Tidak ditemukan"
								if group.invitee is None:
									groupPending = "0"
								else:
									groupPending = str(len(group.invitee))
								if group.preventedJoinByTicket == True:
									groupQr = "Tertutup"
									groupTicket = "Tidak ada"
								else:
									groupQr = "Terbuka"
									groupTicket = "https://line.me/R/ti/g/{}".format(str(client.reissueGroupTicket(group.id)))
								ret_ = "╭───「 Group Info 」"
								ret_ += "\n├ Nama Group : {}".format(group.name)
								ret_ += "\n├ ID Group : {}".format(group.id)
								ret_ += "\n├ Pembuat : @!"
								ret_ += "\n├ Jumlah Member : {}".format(str(len(group.members)))
								ret_ += "\n├ Jumlah Pending : {}".format(groupPending)
								ret_ += "\n├ Group Qr : {}".format(groupQr)
								ret_ += "\n├ Group Ticket : {}".format(groupTicket)
								ret_ += "\n╰───────────"
								client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus))
								client.sendMention(to, str(ret_), [groupCreator])
							except:
								ret_ = "╭───「 Group Info 」"
								ret_ += "\n├ Nama Group : {}".format(group.name)
								ret_ += "\n├ ID Group : {}".format(group.id)
								ret_ += "\n├ Pembuat : {}".format(groupCreator)
								ret_ += "\n├ Jumlah Member : {}".format(str(len(group.members)))
								ret_ += "\n├ Jumlah Pending : {}".format(groupPending)
								ret_ += "\n├ Group Qr : {}".format(groupQr)
								ret_ += "\n├ Group Ticket : {}".format(groupTicket)
								ret_ += "\n╰───────────"
								client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(group.pictureStatus))
								client.sendReplyMessage(msg.id, to, str(ret_))
						elif cmd.startswith("groupbroadcast: "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							groups = client.getGroupIdsJoined()
							for group in groups:
								client.sendMessage(group, "[ Broadcast ]\n{}".format(str(txt)))
							client.sendReplyMessage(msg.id, to, "「BROADCAST GROUP」\nBerhasil broadcast ke {} group".format(str(len(groups))))
						elif cmd == "lurking on":
							tz = pytz.timezone("Asia/Makassar")
							timeNow = datetime.now(tz=tz)
							day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
							hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
							bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
							hr = timeNow.strftime("%A")
							bln = timeNow.strftime("%m")
							for i in range(len(day)):
								if hr == day[i]: hasil = hari[i]
							for k in range(0, len(bulan)):
								if bln == str(k): bln = bulan[k-1]
							readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
							if to in read['readPoint']:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								read['readPoint'][to] = msg_id
								read['readMember'][to] = []
								client.sendReplyMessage(msg.id, to, "「LURKING」\nLurking telah diaktifkan")
							else:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								read['readPoint'][to] = msg_id
								read['readMember'][to] = []
								client.sendReplyMessage(msg.id, to, "Set reading point : \n{}".format(readTime))
						elif cmd == "lurking off":
							tz = pytz.timezone("Asia/Makassar")
							timeNow = datetime.now(tz=tz)
							day = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday"]
							hari = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
							bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
							hr = timeNow.strftime("%A")
							bln = timeNow.strftime("%m")
							for i in range(len(day)):
								if hr == day[i]: hasil = hari[i]
							for k in range(0, len(bulan)):
								if bln == str(k): bln = bulan[k-1]
							readTime = hasil + ", " + timeNow.strftime('%d') + " - " + bln + " - " + timeNow.strftime('%Y') + "\nJam : [ " + timeNow.strftime('%H:%M:%S') + " ]"
							if to not in read['readPoint']:
								client.sendReplyMessage(msg.id, to,"「LURKING」\nLurking telah dinonaktifkan")
							else:
								try:
									del read['readPoint'][to]
									del read['readMember'][to]
								except:
									pass
								client.sendReplyMessage(msg.id, to, "「LURKING」\nDelete reading point : \n{}".format(readTime))
						elif cmd == "lurking":
							if to in read['readPoint']:
								if read["readMember"][to] == []:
									return client.sendReplyMessage(msg.id, to, "「LURKING」\nTidak Ada Sider")
								else:
									no = 0
									result = "╭───「 Reader 」"
									for dataRead in read["readMember"][to]:
										no += 1
										result += "\n├ {}. @!".format(str(no))
									result += "\n╰──「 {} Readet 」".format(str(len(read["readMember"][to])))
									client.sendMention(to, result, read["readMember"][to])
									read['readMember'][to] = []
						elif cmd == "sider on":
							try:
								del cctv['point'][to]
								del cctv['sidermem'][to]
								del cctv['cyduk'][to]
							except:
								pass
							cctv['point'][to] = msg.id
							cctv['sidermem'][to] = ""
							cctv['cyduk'][to]=True
							client.sendReplyMessage(msg.id, to, "SIDER MEMBER MODE ON")
						elif cmd == "sider off":
							if to in cctv['point']:
								cctv['cyduk'][to]=False
								client.sendReplyMessage(msg.id, to, "SIDER MEMBER MODE OFF")
							else:
								client.sendReplyMessage(msg.id, to, "SIDER MEMBER MODE OFF")
						elif cmd == "changepp":
							settings["changePictureProfile"] = True
							client.sendReplyMessage(msg.id, to, "「CHANGE PICTURE PROFILE」\nSilahkan kirim gambarnya")
						elif cmd == "changevp":
							settings["changevp"] = True
							client.sendReplyMessage(msg.id, to, "「CHANGE VIDEO PROFILE」\nKirim video")
						elif cmd == "offchangepp":
							settings["changePictureProfile"] = False
							client.sendReplyMessage(msg.id, to, "「CHANGE PICTURE PROFILE」mode off")
						elif cmd == "offchangevp":
							settings["changevp"] = False
							client.sendReplyMessage(msg.id, to, "「CHANGE VIDEO PROFILE」mode off")
						elif cmd == "changegp":
							if msg.toType == 2:
								if to not in settings["changeGroupPicture"]:
									settings["changeGroupPicture"].append(to)
								client.sendReplyMessage(msg.id, to, "「CHANGE PICTURE PROFILE」\nSilahkan kirim gambarnya")
						elif cmd == "mimic on":
							if settings["mimic"]["status"] == True:
								client.sendReplyMessage(msg.id, to, "「MIMIC」\nReply message telah aktif")
							else:
								settings["mimic"]["status"] = True
								client.sendReplyMessage(msg.id, to, "「MIMIC」\nBerhasil mengaktifkan reply message")
						elif cmd == "mimic off":
							if settings["mimic"]["status"] == False:
								client.sendReplyMessage(msg.id, to, "「MIMIC」\nReply message telah nonaktif")
							else:
								settings["mimic"]["status"] = False
								client.sendReplyMessage(msg.id, to, "「MIMIC」\nBerhasil menonaktifkan reply message")
						elif cmd == "mimiclist":
							if settings["mimic"]["target"] == {}:
								client.sendReplyMessage(msg.id, to, "「MIMIC」\nTidak Ada Target")
							else:
								no = 0
								result = "╭───「 Mimic List 」"
								target = []
								for mid in settings["mimic"]["target"]:
									target.append(mid)
									no += 1
									result += "\n├ {}. @!".format(no)
								result += "\n╰───「 {} Mimic 」".format(str(len(target)))
								client.sendMention(to, result, target)
						elif cmd.startswith("mimicadd "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									try:
										if ls in settings["mimic"]["target"]:
											client.sendReplyMessage(msg.id, to, "「MIMIC」\nTarget sudah ada dalam list")
										else:
											settings["mimic"]["target"][ls] = True
											client.sendReplyMessage(msg.id, to, "「MIMIC」\nBerhasil menambahkan target")
									except:
										client.sendReplyMessage(msg.id, to, "「MIMIC」\nGagal menambahkan target")
						elif cmd.startswith("mimicdel "):
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								lists = []
								for mention in mentionees:
									if mention["M"] not in lists:
										lists.append(mention["M"])
								for ls in lists:
									try:
										if ls not in settings["mimic"]["target"]:
											client.sendReplyMessage(msg.id, to, "「MIMIC」\nTarget sudah tida didalam list")
										else:
											del settings["mimic"]["target"][ls]
											client.sendReplyMessage(msg.id, to, "「MIMIC」\nBerhasil menghapus target")
									except:
										client.sendReplyMessage(msg.id, to, "「MIMIC」\nGagal menghapus target")
						elif cmd.startswith("instainfo"):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							url = requests.get("http://rahandiapi.herokuapp.com/instainfo/{}?key=betakey".format(txt))
							data = url.json()
							icon = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/599px-Instagram_icon.png"
							name = "Instagram"
							link = "https://www.instagram.com/{}".format(data["result"]["username"])
							result = "╭───「 InstagramInfo 」"
							result += "\n├ Name : {}".format(data["result"]["name"])
							result += "\n├ Username: {}".format(data["result"]["username"])
							result += "\n├ Bio : {}".format(data["result"]["bio"])
							result += "\n├ Follower : {}".format(data["result"]["follower"])
							result += "\n├ Following : {}".format(data["result"]["following"])
							result += "\n├ Private : {}".format(data["result"]["private"])
							result += "\n├ Post : {}".format(data["result"]["mediacount"])
							result += "\n╰───────────"
							client.sendImageWithURL(to, data["result"]["url"])
							client.sendFooter(to, result, icon, name, link)
						elif cmd.startswith("instastory "):
							sep = text.split(" ")
							query = text.replace(sep[0] + " ","")
							cond = query.split("|")
							search = str(cond[0])
							if len(cond) == 2:
								url = requests.get("https://rahandiapi.herokuapp.com/instastory/{}?key=betakey".format(search))
								data = url.json()
								num = int(cond[1])
								if num <= len(data["url"]):
									search = data["url"][num - 1]
									if search["tipe"] == 1:
										client.sendImageWithURL(to, str(search["link"]))
									elif search["tipe"] == 2:
										client.sendVideoWithURL(to, str(search["link"]))
						elif cmd.startswith("youtubemp3 "):
								sep = msg.text.split(" ")
								textToSearch = msg.text.replace(sep[0] + " ","")
								query = urllib.parse.quote(textToSearch)
								search_url="https://www.youtube.com/results?search_query="
								mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
								sb_url = search_url + query
								sb_get = requests.get(sb_url, headers = mozhdr)
								soupeddata = BeautifulSoup(sb_get.content, "html.parser")
								yt_links = soupeddata.find_all("a", class_ = "yt-uix-tile-link")
								x = (yt_links[1])
								yt_href =  x.get("href")
								yt_href = yt_href.replace("watch?v=", "")
								qx = "https://youtu.be" + str(yt_href)
								vid = pafy.new(qx)
								stream = vid.streams
								best = vid.getbest()
								best.resolution, best.extension
								for s in stream:
									me = best.url
								client.sendAudioWithURL(msg.to, me)
						elif cmd.startswith("youtubemp4 "):
								sep = msg.text.split(" ")
								textToSearch = msg.text.replace(sep[0] + " ","")
								query = urllib.parse.quote(textToSearch)
								search_url="https://www.youtube.com/results?search_query="
								mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
								sb_url = search_url + query
								sb_get = requests.get(sb_url, headers = mozhdr)
								soupeddata = BeautifulSoup(sb_get.content, "html.parser")
								yt_links = soupeddata.find_all("a", class_ = "yt-uix-tile-link")
								x = (yt_links[1])
								yt_href =  x.get("href")
								yt_href = yt_href.replace("watch?v=", "")
								qx = "https://youtu.be" + str(yt_href)
								vid = pafy.new(qx)
								stream = vid.streams
								best = vid.getbest()
								best.resolution, best.extension
								for s in stream:
									me = best.url
								client.sendVideoWithURL(msg.to, me)
						elif cmd.startswith("searchyoutube "):
							sep = text.split(" ")
							txt = msg.text.replace(sep[0] + " ","")
							cond = txt.split("|")
							search = cond[0]
							url = requests.get("https://api.w3hills.com/youtube/search?keyword={}&api_key=86A7FCF3-6CAF-DEB9-E214-B74BDB835B5B".format(search))
							data = url.json()
							if len(cond) == 1:
								no = 0
								result = "╭───「 Youtube 」"
								for anu in data["videos"]:
									no += 1
									result += "\n├ {}. {}".format(str(no),str(anu["title"]))
								result += "\n╰──「 {} Result 」".format(str(len(data["videos"])))
								client.sendReplyMessage(msg.id, to, result)
							elif len(cond) == 2:
								num = int(str(cond[1]))
								if num <= len(data):
									search = data["videos"][num - 1]
									ret_ = "╭───「 Youtube Info 」"
									ret_ += "\n├ Channel : {}".format(str(search["publish"]["owner"]))
									ret_ += "\n├ Title : {}".format(str(search["title"]))
									ret_ += "\n├ Release : {}".format(str(search["publish"]["date"]))
									ret_ += "\n├ Viewers : {}".format(str(search["stats"]["views"]))
									ret_ += "\n├ Likes : {}".format(str(search["stats"]["likes"]))
									ret_ += "\n├ Dislikes : {}".format(str(search["stats"]["dislikes"]))
									ret_ += "\n├ Rating : {}".format(str(search["stats"]["rating"]))
									ret_ += "\n├ Description : {}".format(str(search["description"]))
									ret_ += "\n╰───────────"
									client.sendImageWithURL(to, str(search["thumbnail"]))
									client.sendReplyMessage(msg.id, to, str(ret_))
						elif cmd.startswith("smule "):
							proses = text.split(" ")
							urutan = text.replace(proses[0] + " ","")
							count = urutan.split("-")
							search = str(count[0])
							r = requests.get("https://www.smule.com/"+search+"/performances/json")
							data = json.loads(r.text)
							if len(count) == 1:
								no = 0
								ret_ = "DAFTAR OC\n"
								for aa in data["list"]:
									no += 1
									ret_ += "\n" + str(no) + ". " + str(aa["title"])
								ret_ += "\n\nSelanjutnya ketik: smule {}-nomor\nuntuk melihat detailnya. ".format(str(search))
								client.sendMessage(msg.to,ret_)
							elif len(count) == 2:
								try:
									num = int(count[1])
									b = data["list"][num - 1]
									smule = str(b["web_url"])
									c = "Judul Oc: "+str(b["title"])
									c += "\nPembuat: "+str(b["owner"]["handle"])
									c += "\nTotal like: "+str(b["stats"]["total_loves"])+" like"
									c += "\nTotal comment: "+str(b["stats"]["total_comments"])+" comment"
									c += "\nStatus VIP: "+str(b["owner"]["is_vip"])
									c += "\nStatus Oc: "+str(b["message"])
									c += "\nCreated Oc: {}".format(b["created_at"][:10])
									c += "\nDidengarkan: {}".format(b["stats"]["total_listens"])+" orang"
									hasil = "Detail Record\n\n"+str(c)
									dl = str(b["cover_url"])
									client.sendImageWithURL(msg.to,dl)
									client.sendMessage(msg.to, hasil, {'AGENT_NAME': ' URL Smule','AGENT_LINK': 'https://www.smule.com/{}'.format(str(b['owner']['handle'])),'AGENT_ICON': 'https://png.icons8.com/color/50/000000/speaker.png' })
									with requests.session() as s:
										s.headers['user-agent'] = 'Mozilla/5.0'
										r = s.get("https://sing.salon/smule-downloader/?url=https://www.smule.com{}".format(urllib.parse.quote(smule)))
										data = BeautifulSoup(r.content, 'html5lib')
										get = data.select("a[href*=https://www.smule.com/redir?]")[0]
										title = data.findAll('h2')[0].text
										imag = data.select("img[src*=https://www.smule.com/redir?]")[0]
										if 'Smule.m4a' in get['download']:
											client.sendMessage(msg.to,"Type: Audio\n\nPlease wait for audio...")
											client.sendAudioWithURL(msg.to, get['href'])
										else:
											client.sendMessage(msg.to,"Type: Video\n\nPlease wait for video...")
											client.sendVideoWithURL(msg.to, get['href'])
								except Exception as e:
									client.sendMessage(msg.to,"DONE")
						elif cmd.startswith("searchimage "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							url = requests.get("https://rahandiapi.herokuapp.com/imageapi?key=betakey&q={}".format(txt))
							data = url.json()
							client.sendImageWithURL(to, random.choice(data["result"]))
						elif cmd.startswith("music "):
							sep = text.split(" ")
							query = text.replace(sep[0] + " ","")
							cond = query.split("|")
							search = str(cond[0])
							url = requests.get("https://api.fckveza.com/jooxmusic={}".format(str(search)))
							data = url.json()
							if len(cond) == 1:
								num = 0
								ret_ = "╭───「 Music 」]"
								for music in data["result"]:
									num += 1
									ret_ += "\n├ {}. {}".format(str(num), str(music["judul"]))
								ret_ += "\n╰──「 {} Music 」".format(str(len(data["result"])))
								ret_ += "\n\nUntuk mengirim music, silahkan gunakan command {} Music {}|「number」".format(str(setKey), str(search))
								client.sendReplyMessage(msg.id, to, str(ret_))
							elif len(cond) == 2:
								num = int(cond[1])
								if num <= len(data["result"]):
									music = data["result"][num - 1]
									url = requests.get("https://api.fckveza.com/musicid={}".format(str(music["songid"])))
									data = url.json()
									ret_ = "╭───「 Result 」"
									ret_ += "\n├ Title : {}".format(str(data["result"]["judul"]))
									ret_ += "\n├ Artis : {}".format(str(data["result"]["artis"]))
									ret_ += "\n├ Size : {}".format(str(data["result"]["size"]))
									ret_ += "\n├ Link : {}".format(str(data["result"]["mp3"][0]))
									ret_ += "\n╰───────────"
									client.sendImageWithURL(to, str(data["result"]["imgUrl"]))
									client.sendReplyMessage(msg.id, to, str(ret_))
									client.sendAudioWithURL(to, str(data["result"]["mp3Url"][0]))
						elif cmd.startswith("searchlyric "):
							sep = text.split(" ")
							txt = text.replace(sep[0] + " ","")
							cond = txt.split("|")
							query = cond[0]
							with requests.session() as web:
								web.headers["user-agent"] = "Mozilla/5.0"
								url = web.get("https://www.musixmatch.com/search/{}".format(urllib.parse.quote(query)))
								data = BeautifulSoup(url.content, "html.parser")
								result = []
								for trackList in data.findAll("ul", {"class":"tracks list"}):
									for urlList in trackList.findAll("a"):
										title = urlList.text
										url = urlList["href"]
										result.append({"title": title, "url": url})
								if len(cond) == 1:
									ret_ = "╭───「 Lyric 」"
									num = 0
									for title in result:
										num += 1
										ret_ += "\n├ {}. {}".format(str(num), str(title["title"]))
									ret_ += "\n╰───「 Lyric 」".format(str(len(result)))
									ret_ += "\n\nUntuk melihat lyric, silahkan gunakan command {}SearchLyric {}|「number」".format(str(setKey), str(query))
									client.sendReplyMessage(msg.id, to, ret_)
								elif len(cond) == 2:
									num = int(cond[1])
									if num <= len(result):
										data = result[num - 1]
										with requests.session() as web:
											web.headers["user-agent"] = "Mozilla/5.0"
											url = web.get("https://www.musixmatch.com{}".format(urllib.parse.quote(data["url"])))
											data = BeautifulSoup(url.content, "html5lib")
											for lyricContent in data.findAll("p", {"class":"mxm-lyrics__content "}):
												lyric = lyricContent.text
												client.sendReplyMessage(msg.id, to, lyric)
						
						if text.lower() == "mykey":
							client.sendReplyMessage(msg.id, to, "「KEY」\nKeycommand : 「{}」".format(str(settings["keyCommand"])))
						elif text.lower() == "setkey on":
							if settings["setKey"] == True:
								client.sendReplyMessage(msg.id, to, "「SET KEY」\nSetkey telah aktif")
							else:
								settings["setKey"] = True
								client.sendReplyMessage(msg.id, to, "「SET KEY」\nBerhasil mengaktifkan setkey")
						elif text.lower() == "setkey off":
							if settings["setKey"] == False:
								client.sendReplyMessage(msg.id, to, "「SET KEY」\nSetkey telah nonaktif")
							else:
								settings["setKey"] = False
								client.sendReplyMessage(msg.id, to, "「SET KEY」\nBerhasil menonaktifkan setkey")
						if text is None: return
						if "/ti/g/" in msg.text.lower():
							if settings["autoJoinTicket"] == True:
								link_re = re.compile('(?:line\:\/|line\.me\/R)\/ti\/g\/([a-zA-Z0-9_-]+)?')
								links = link_re.findall(text)
								n_links = []
								for l in links:
									if l not in n_links:
										n_links.append(l)
								for ticket_id in n_links:
									group = client.findGroupByTicket(ticket_id)
									client.acceptGroupInvitationByTicket(group.id,ticket_id)
									client.sendReplyMessage(msg.id, to, "Berhasil masuk ke group %s" % str(group.name))
					elif msg.contentType == 1:
						if settings["changePictureProfile"] == True:
							path = client.downloadObjectMsg(msg_id, saveAs="LineAPI/tmp/{}-cpp.bin".format(time.time()))
							settings["changePictureProfile"] = False
							client.updateProfilePicture(path)
							client.sendReplyMessage(msg.id, to, "Berhasil mengubah foto profile")
							client.deleteFile(path)
						if msg.toType == 2:
							if to in settings["changeGroupPicture"]:
								path = client.downloadObjectMsg(msg_id, saveAs="LineAPI/tmp/{}-cgp.bin".format(time.time()))
								settings["changeGroupPicture"].remove(to)
								client.updateGroupPicture(to, path)
								client.sendReplyMessage(msg.id, to, "Berhasil mengubah foto group")
								client.deleteFile(path)
					elif msg.contentType == 2:
						if settings["changevp"] == True:
							contact = client.getProfile()
							path = client.downloadFileURL("https://obs.line-scdn.net/{}".format(contact.pictureStatus))
							path1 = client.downloadObjectMsg(msg_id)
							settings["changevp"] = False
							changeVideoAndPictureProfile(path, path1)
							client.sendReplyMessage(msg.id, to, "Success change video profile")
					elif msg.contentType == 7:
						if settings["checkSticker"] == True:
							stk_id = msg.contentMetadata['STKID']
							stk_ver = msg.contentMetadata['STKVER']
							pkg_id = msg.contentMetadata['STKPKGID']
							ret_ = "╭───「 Sticker Info 」"
							ret_ += "\n├ STICKER ID : {}".format(stk_id)
							ret_ += "\n├ STICKER PACKAGES ID : {}".format(pkg_id)
							ret_ += "\n├ STICKER VERSION : {}".format(stk_ver)
							ret_ += "\n├ STICKER URL : line://shop/detail/{}".format(pkg_id)
							ret_ += "\n╰───────────"
							client.sendReplyMessage(msg.id, to, str(ret_))
					elif msg.contentType == 13:
						if settings["checkContact"] == True:
							try:
								contact = client.getContact(msg.contentMetadata["mid"])
								cover = client.getProfileCoverURL(msg.contentMetadata["mid"])
								ret_ = "╭───「 Details 」"
								ret_ += "\n├ Nama : {}".format(str(contact.displayName))
								ret_ += "\n├ MID : {}".format(str(msg.contentMetadata["mid"]))
								ret_ += "\n├ Bio : {}".format(str(contact.statusMessage))
								ret_ += "\n├ Gambar Profile : http://dl.profile.line-cdn.net/{}".format(str(contact.pictureStatus))
								ret_ += "\n├ Gambar Cover : {}".format(str(cover))
								ret_ += "\n╰───────────"
								client.sendImageWithURL(to, "http://dl.profile.line-cdn.net/{}".format(str(contact.pictureStatus)))
								client.sendReplyMessage(msg.id, to, str(ret_))
							except:
								client.sendReplyMessage(msg.id, to, "Kontak tidak valid")
					
					elif msg.contentType == 16:
						if settings["checkPost"] == True:
							try:
								ret_ = "╭───「 Post 」"
								if msg.contentMetadata["serviceType"] == "GB":
									contact = client.getContact(sender)
									auth = "\n├ Penulis : {}".format(str(contact.displayName))
								else:
									auth = "\n├ Penulis : {}".format(str(msg.contentMetadata["serviceName"]))
								purl = "\n├ URL : {}".format(str(msg.contentMetadata["postEndUrl"]).replace("line://","https://line.me/R/"))
								ret_ += auth
								ret_ += purl
								if "mediaOid" in msg.contentMetadata:
									object_ = msg.contentMetadata["mediaOid"].replace("svc=myhome|sid=h|","")
									if msg.contentMetadata["mediaType"] == "V":
										if msg.contentMetadata["serviceType"] == "GB":
											ourl = "\n├ Objek URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(msg.contentMetadata["mediaOid"]))
											murl = "\n├ Media URL : https://obs-us.line-apps.com/myhome/h/download.nhn?{}".format(str(msg.contentMetadata["mediaOid"]))
										else:
											ourl = "\n├ Objek URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(object_))
											murl = "\n├ Media URL : https://obs-us.line-apps.com/myhome/h/download.nhn?{}".format(str(object_))
										ret_ += murl
									else:
										if msg.contentMetadata["serviceType"] == "GB":
											ourl = "\n├ Objek URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(msg.contentMetadata["mediaOid"]))
										else:
											ourl = "\n├ Objek URL : https://obs-us.line-apps.com/myhome/h/download.nhn?tid=612w&{}".format(str(object_))
									ret_ += ourl
								if "stickerId" in msg.contentMetadata:
									stck = "\n├ Stiker : https://line.me/R/shop/detail/{}".format(str(msg.contentMetadata["packageId"]))
									ret_ += stck
								if "text" in msg.contentMetadata:
									text = "\n├ Tulisan : {}".format(str(msg.contentMetadata["text"]))
									ret_ += text
								ret_ += "\n╰───────────"
								client.sendReplyMessage(msg.id, to, str(ret_))
							except:
								client.sendReplyMessage(msg.id, to, "Post tidak valid")
			except Exception as error:
				logError(error)


		if op.type == 26:
			try:
				msg = op.message
				text = str(msg.text)
				msg_id = msg.id
				receiver = msg.to
				sender = msg._from
				if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
					if msg.toType == 0:
						if sender != client.profile.mid:
							to = sender
						else:
							to = receiver
					elif msg.toType == 1:
						to = receiver
					elif msg.toType == 2:
						to = receiver
					if sender in settings["mimic"]["target"] and settings["mimic"]["status"] == True and settings["mimic"]["target"][sender] == True:
						if msg.contentType == 0:
							client.sendReplyMessage(msg.id, to, text)
						elif msg.contentType == 1:
							path = client.downloadObjectMsg(msg_id, saveAs="LineAPI/tmp/{}-mimic.bin".format(time.time()))
							client.sendImage(to, path)
							client.deleteFile(path)
					if msg.contentType == 0:
						if settings["autoRead"] == True:
							if sender not in whitelist:
								client.sendChatChecked(to, msg_id)
						if sender not in clientMid:
							if msg.toType != 0 and msg.toType == 2:
								if 'MENTION' in msg.contentMetadata.keys()!= None:
									names = re.findall(r'@(\w+)', text)
									mention = ast.literal_eval(msg.contentMetadata['MENTION'])
									mentionees = mention['MENTIONEES']
									for mention in mentionees:
										if clientMid in mention["M"]:
											if settings["autoRespon"] == True:
												client.sendMention(sender, settings["autoResponMessage"], [sender])
											break
						if text is None: return
						if "/ti/g/" in msg.text.lower():
							if settings["autoJoinTicket"] == True:
								link_re = re.compile('(?:line\:\/|line\.me\/R)\/ti\/g\/([a-zA-Z0-9_-]+)?')
								links = link_re.findall(text)
								n_links = []
								for l in links:
									if l not in n_links:
										n_links.append(l)
								for ticket_id in n_links:
									group = client.findGroupByTicket(ticket_id)
									client.acceptGroupInvitationByTicket(group.id,ticket_id)
									client.sendReplyMessage(msg.id, to, "Berhasil masuk ke group %s" % str(group.name))
						if to in detectUnsend:
							try:
								unsendTime = time.time()
								unsend[msg_id] = {"text": text, "from": sender, "time": unsendTime}
							except Exception as error:
								logError(error)
					if msg.contentType == 1:
						if to in detectUnsend:
							try:
								unsendTime = time.time()
								image = client.downloadObjectMsg(msg_id, saveAs="LineAPI/tmp/{}-image.bin".format(time.time()))
								unsend[msg_id] = {"from": sender, "image": image, "time": unsendTime}
							except Exception as error:
								logError(error)
			except Exception as error:
				logError(error)

		if op.type == 55:
			if op.param1 in read["readPoint"]:
				if op.param2 not in read["readMember"][op.param1]:
					read["readMember"][op.param1].append(op.param2)
					
			if cctv['cyduk'][op.param1]==True:
				Name = client.getContact(op.param2).displayName
				if Name in cctv['sidermem'][op.param1]:
					pass
				else:
					cctv['sidermem'][op.param1] += "\n~ " + Name
					siderMembers(op.param1, [op.param2])
					pict = client.getContact(op.param2).picturePath
					image = 'http://dl.profile.line-cdn.net'+pict
					client.sendImageWithURL(op.param1, image)
		if op.type == 26:
			try:
				msg = op.message
				text = str(msg.text)
				msg_id = msg.id
				receiver = msg.to
				sender = msg._from
				if msg.toType == 0 or msg.toType == 1 or msg.toType == 2:
					if msg.toType == 0:
						if sender != client.profile.mid:
							to = sender
						else:
							to = receiver
					elif msg.toType == 1:
						to = receiver
					elif msg.toType == 2:
						to = receiver
					if msg.contentType == 0:
						if msg.toType != 0 and msg.toType == 2:
							if 'MENTION' in msg.contentMetadata.keys()!= None:
								names = re.findall(r'@(\w+)', text)
								mention = ast.literal_eval(msg.contentMetadata['MENTION'])
								mentionees = mention['MENTIONEES']
								for mention in mentionees:
									if clientMid in mention["M"]:
										if client.getProfile().mid in mention["M"]:
											if to not in tagme['ROM']:
												tagme['ROM'][to] = {}
											if sender not in tagme['ROM'][to]:
												tagme['ROM'][to][sender] = {}
											if 'msg.id' not in tagme['ROM'][to][sender]:
												tagme['ROM'][to][sender]['msg.id'] = []
											if 'waktu' not in tagme['ROM'][to][sender]:
												tagme['ROM'][to][sender]['waktu'] = []
											tagme['ROM'][to][sender]['msg.id'].append(msg.id)
											tagme['ROM'][to][sender]['waktu'].append(msg.createdTime)
			except Exception as error:
				logError(error)

		if op.type == 65:
			try:
				if op.param1 in detectUnsend:
					to = op.param1
					sender = op.param2
					if sender in unsend:
						unsendTime = time.time()
						contact = client.getContact(unsend[sender]["from"])
						if "text" in unsend[sender]:
							try:
								sendTime = unsendTime - unsend[sender]["time"]
								sendTime = timeChange(sendTime)
								ret_ = "╭───「 Unsend Message 」"
								ret_ += "\n├ Sender : @!"
								ret_ += "\n├ Time : {} yang lalu".format(sendTime)
								ret_ += "\n├ Type : Text"
								ret_ += "\n├ Text : {}".format(unsend[sender]["text"])
								ret_ += "\n╰───────────"
								client.sendMention(to, ret_, [contact.mid])
								del unsend[sender]
							except:
								del unsend[sender]
						elif "image" in unsend[sender]:
							try:
								sendTime = unsendTime - unsend[sender]["time"]
								sendTime = timeChange(sendTime)
								ret_ = "╭───「 Unsend Image 」"
								ret_ += "\n├ Sender : @!"
								ret_ += "\n├ Time : {} yang lalu".format(sendTime)
								ret_ += "\n├ Type : Image"
								ret_ += "\n├ Text : None"
								ret_ += "\n╰───────────"
								client.sendMention(to, ret_, [contact.mid])
								client.sendImage(to, unsend[sender]["image"])
								client.deleteFile(unsend[sender]["image"])
								del unsend[sender]
							except:
								client.deleteFile(unsend[sender]["image"])
								del unsend[sender]
					else:
						client.sendReplyMessage(msg.id, to, "Data unsend tidak ditemukan")
			except Exception as error:
				logError(error)
		backupData()
	except Exception as error:
		logError(error)
	
def menuHelp():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuHelp =	"╭───「 Bots 」" + "\n" + \
				"├ " + key + "Me" + "\n" + \
				"├ " + key + "Mentionall" + "\n" + \
				"├ " + key + "Mentionme" + "\n" + \
				"├ " + key + "Delmentionme" + "\n" + \
				"├ " + key + "FriendList" + "\n" + \
				"├ " + key + "FriendInfo 「Num」" + "\n" + \
				"├ " + key + "FriendBroadcast" + "\n" + \
				"├ " + key + "Lurking 「On/Off」" + "\n" + \
				"├ " + key + "Lurking" + "\n" + \
				"├ " + key + "CloneProfile 「@」" + "\n" + \
				"├ " + key + "RestoreProfile" + "\n" + \
				"├ " + key + "BackupProfile" + "\n" + \
				"├ " + key + "Speed" + "\n" + \
				"├ " + key + "Runtime" + "\n" + \
				"├ " + key + "Restart" + "\n" + \
				"├ " + key + "Logout" + "\n" + \
				"╰────────────"
	return menuHelp

def menuMy():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuMy =	"╭────「 Profile 」" + "\n" + \
				"├   「 Send Mid 」" + "\n" + \
				"├ " + key + "MyMid" + "\n" + \
				"├   「 Send Name 」" + "\n" + \
				"├ " + key + "MyName" + "\n" + \
				"├   「 Send Bio 」" + "\n" + \
				"├ " + key + "MyBio" + "\n" + \
				"├   「 Send Picture 」" + "\n" + \
				"├ " + key + "MyPicture" + "\n" + \
				"├   「 Send Video Profile 」" + "\n" + \
				"├ " + key + "MyVideo" + "\n" + \
				"├   「 Send Cover Profile 」" + "\n" + \
				"├ " + key + "MyCover" + "\n" + \
				"├   「 Send Profile 」" + "\n" + \
				"├ " + key + "MyProfile" + "\n" + \
				"╰────────────"
	return menuMy

def menuGet():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuGet =	"╭───「 Steal 」" + "\n" + \
				"├   「 Send Mid Target 」" + "\n" + \
				"├ " + key + "GetMid 「@」" + "\n" + \
				"├   「 Send Name Target 」" + "\n" + \
				"├ " + key + "GetName 「@」" + "\n" + \
				"├   「 Send Bio Target 」" + "\n" + \
				"├ " + key + "GetBio 「@」" + "\n" + \
				"├   「 Send Picture Target 」" + "\n" + \
				"├ " + key + "GetPicture 「@」" + "\n" + \
				"├   「 Send Video Target 」" + "\n" + \
				"├ " + key + "GetVideoProfile 「@」" + "\n" + \
				"├   「 Send Cover Target 」" + "\n" + \
				"├ " + key + "GetCover 「@」" + "\n" + \
				"├────────────" + "\n" + \
				"├───「 Note 」" + "\n" + \
				"├[Mention] : 「@」" + "\n" + \
				"╰────────────"
	return menuGet
	
def menuGroup():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuGroup =	"╭───「 Group 」" + "\n" + \
				"├「 Send Group ID 」" + "\n" + \
				"├ " + key + "GroupID" + "\n" + \
				"├「 Send Group Name 」" + "\n" + \
				"├ " + key + "GroupName" + "\n" + \
				"├「 Send Group Picture 」" + "\n" + \
				"├ " + key + "GroupPicture" + "\n" + \
				"├「 Send Group List 」" + "\n" + \
				"├ " + key + "GroupList" + "\n" + \
				"├「 Send Group Member 」" + "\n" + \
				"├ " + key + "GroupMemberList" + "\n" + \
				"├「 Send Group Pending 」" + "\n" + \
				"├ " + key + "GroupPendingList" + "\n" + \
				"├「 Send Group Info 」" + "\n" + \
				"├ " + key + "GroupInfo" + "\n" + \
				"├「 Broadcast All Group 」" + "\n" + \
				"├ " + key + "GroupBroadcast: 「Text」" + "\n" + \
				"├「 Set Group Name 」" + "\n" + \
				"├ " + key + "GroupName: 「Text」" + "\n" + \
				"├「 Set Group Picture 」" + "\n" + \
				"├ " + key + "Changegp" + "\n" + \
				"╰────────────"
	return menuGroup
	
def menuMimic():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuMimic =	"╭───「 Mimic 」" + "\n" + \
				"├ " + key + "Mimic 「/」" + "\n" + \
				"├ " + key + "MimicList" + "\n" + \
				"├ " + key + "MimicAdd 「@」" + "\n" + \
				"├ " + key + "MimicDel 「@」" + "\n" + \
				"├────────────" + "\n" + \
				"├───「 Note 」" + "\n" + \
				"├[On/Off] : 「/」" + "\n" + \
				"├[Mention] : 「@」" + "\n" + \
				"╰────────────"
	return menuMimic

def menuHelp1():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuHelp1 =	"╭───「 SelfBot 」" + "\n" + \
	            "├ " + key + "Favorite" + "\n" + \
				"├ " + key + "Help1" + "\n" + \
				"├ " + key + "Help2" + "\n" + \
				"├ " + key + "Help3" + "\n" + \
				"├ " + key + "Help4" + "\n" + \
				"├ " + key + "Help5" + "\n" + \
				"├ " + key + "Help6" + "\n" + \
				"├ " + key + "Help7" + "\n" + \
				"├ " + key + "Status" + "\n" + \
				"├ " + key + "Settings" + "\n" + \
				"├────────────" + "\n" + \
				"├ DPK - SELBOT" + "\n" + \
				"╰────────────"
	return menuHelp1
	
def menuFav():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuFav =	"╭──「 Top Features 」" + "\n" + \
				"├ " + key + "Mentionall" + "\n" + \
				"├ " + key + "Lurking 「On/Off」" + "\n" + \
				"├ " + key + "Lurking" + "\n" + \
				"├ " + key + "Sider 「On/Off」" + "\n" + \
				"├ " + key + "Smule 「ID」" + "\n" + \
				"├ " + key + "Youtubemp3 「Judul」" + "\n" + \
				"├ " + key + "Youtubemp4 「Judul」" + "\n" + \
				"├ " + key + "Groupbroadcast: (Msg)" + "\n" + \
				"├ " + key + "Detectunsend ON/OFF" + "\n" + \
				"├ " + key + "Autorespon ON/OFF" + "\n" + \
				"├「 Spam Mention Target 」" + "\n" + \
				"├ " + key + "Spamtag 「*」 「@」" + "\n" + \
				"├「 Spam Text 」" + "\n" + \
				"├ " + key + "Spamtext 「/」 「*」 「+」" + "\n" + \
				"├───「 Note 」" + "\n" + \
				"├[On/Off] : 「/」" + "\n" + \
				"├[Number] : 「*」" + "\n" + \
				"├[Mention] : 「@」" + "\n" + \
				"├[Text] : 「+」" + "\n" + \
				"├────────────" + "\n" + \
				"├ " + key + "Dell 「removechat」" + "\n" + \
				"├ " + key + "Speed" + "\n" + \
				"├ " + key + "Runtime" + "\n" + \
				"├ " + key + "Restart" + "\n" + \
				"├ " + key + "Logout" + "\n" + \
				"╰────────────"
	return menuFav
	
def menuChange():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuChange =	"╭───「 Profile 」" + "\n" + \
				"├「 Change Your Name 」" + "\n" + \
				"├ " + key + "ChangeName: 「Text」" + "\n" + \
				"├「 Change Your Bio 」" + "\n" + \
				"├ " + key + "ChangeBio: 「Text」" + "\n" + \
				"├「 Change Your Picture 」" + "\n" + \
				"├ " + key + "ChangePP" + "\n" + \
				"├「 Change Your Video 」" + "\n" + \
				"├ " + key + "ChangeVP" + "\n" + \
				"╰────────────"
	return menuChange

def menuSpam():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuSpam =	"╭───「 Spam 」" + "\n" + \
				"├「 Spam Mention Target 」" + "\n" + \
				"├ " + key + "Spamtag 「*」 「@」" + "\n" + \
				"├「 Spam Call Group 」" + "\n" + \
				"├ " + key + "Spamcall 「*」" + "\n" + \
				"├「 Spam Call Private 」" + "\n" + \
				"├ " + key + "Spamcallto 「*」 「@」" + "\n" + \
				"├「 Spam Text 」" + "\n" + \
				"├ " + key + "Spamtext 「/」 「*」 「+」" + "\n" + \
				"├───「 Note 」" + "\n" + \
				"├[On/Off] : 「/」" + "\n" + \
				"├[Number] : 「*」" + "\n" + \
				"├[Mention] : 「@」" + "\n" + \
				"├[Text] : 「+」" + "\n" + \
				"╰────────────"
	return menuSpam
	
def menuStatus():
	if settings['setKey'] == True:
		key = settings['keyCommand']
	else:
		key = ''
	menuStatus =	"╭───「 Settings 」" + "\n" + \
				"├ " + key + "AutoAdd 「/」" + "\n" + \
				"├ " + key + "AutoJoin 「/」" + "\n" + \
				"├ " + key + "AutoJoinTicket 「/」" + "\n" + \
				"├ " + key + "AutoRead 「/」" + "\n" + \
				"├ " + key + "AutoRespon 「/」" + "\n" + \
				"├ " + key + "CheckContact 「/」" + "\n" + \
				"├ " + key + "CheckPost 「/」" + "\n" + \
				"├ " + key + "CheckSticker 「/」" + "\n" + \
				"├ " + key + "DetectUnsend 「/」" + "\n" + \
				"├───「 Note 」" + "\n" + \
				"├[On/Off] : 「/」" + "\n" + \
				"╰────────────"
	return menuStatus

def run():
	while True:
		ops = clientPoll.singleTrace(count=50)
		if ops != None:
			for op in ops:
				try:
					clientBot(op)
				except Exception as error:
					logError(error)
				clientPoll.setRevision(op.revision)

if __name__ == "__main__":
	run()
