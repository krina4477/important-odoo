Installation Guide
---------------

After Installing this module, 
First Install these 3 packages:
----------------------

sudo pip3 install geoip2
sudo pip3 install python-geoip
sudo pip3 install python-geoip-geolite2

then after depending your server, make changes in /website_region_ip_address/models/region.py line no: 128

If you have are working on local server, then no need to change any code.
but,

If you have a nginx server, then simply comment line no: 128 & uncomment line no: 129.
----------------------

#ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read() # This Code is working in local server
ip_add = request.httprequest.environ["REMOTE_ADDR"] # This Code is working in nginx server
#ip_add = request.httprequest.environ["HTTP_X_FORWARDED_FOR"] # This Code is working in Apache server

If you have a Apache server, then simply comment line no: 128 & uncomment line no: 130.
----------------------

#ip_add  = os.popen("wget http://ipecho.net/plain -O - -q ; echo").read() # This Code is working in local server
#ip_add = request.httprequest.environ["REMOTE_ADDR"] # This Code is working in nginx server
ip_add = request.httprequest.environ["HTTP_X_FORWARDED_FOR"] # This Code is working in Apache server


Thanks...!!!

