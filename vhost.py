# Works with Python 3
# Python Virtual Host generator script
import sys, os, pwd, grp

# Configs
# enter linux user name
user = 'dilshod'
# enter sites directory path
sites_dir = '/var/www'
# enter sites http directory name
html_dir = 'public_html'
# enter apache vhosts directory path
nginx_hosts = '/etc/nginx/sites-available'

print "Welcome to VirtualHost generator!"
print """This script generates VirtualHost on Nginx . First you have to adjust the script according to your needs. As the script starts working, you will have to enter your virtual domain name.
Note: You have to get root permissions for the script to work."""

def vhostdata( domain ):

	data = """ server {

		charset utf-8;
    		client_max_body_size 128M;

		listen 80;
		listen [::]:80;

		server_name %(domain)s  www.%(domain)s;
		root %(sites_dir)s/%(domain)s/%(html_dir)s/web;
		index index.php;

                access_log  %(sites_dir)s/%(domain)s/logs/access.log;
	        error_log  %(sites_dir)s/%(domain)s/logs/error.log;

	    	location / {location ~*  \.(jpg|jpeg|bmp|png|gif|ico|css|js|JPG|woff|woff2|eot|svg|html|map|json|less|sass|ttf|ttf2|swf|otf|txt|pdf|mp4)$ {
 expires 8d;
}
		# Redirect everything that isn't a real file to index.php
			try_files $uri $uri/ /index.php$is_args$args;
	    	}

	       # uncomment to avoid processing of calls to non-existing static files by Yii
    	       location ~ \.(js|css|png|jpg|gif|swf|ico|pdf|mov|fla|zip|rar)$ {
	       		try_files $uri =404;
               }
               
	       error_page 404 /404.html;

       	      # deny accessing php files for the /assets directory

	      location ~ ^/assets/.*\.php$ {
		   deny all;
	      } 

	      location ~ \.php$ {
		   include snippets/fastcgi-php.conf;
 		   fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
		   fastcgi_pass 127.0.0.1:9000;
		   #fastcgi_pass unix:/var/run/php5-fpm.sock;
		   # try_files $uri =404;
	      }

	      location ~* /\. {
		   deny all;
	      }
		
              location ~*  \.(jpg|jpeg|bmp|png|gif|ico|css|js|JPG|woff|woff2|eot|svg|html|map|json|less|sass|ttf|ttf2|swf|otf|txt|pdf|mp4)$ {
 			expires 8d;
	      }


	} """ % {'domain':domain,'sites_dir':sites_dir,'html_dir':html_dir}

	return data

def vhostcreate(domain):
	if domain:
		confirm = raw_input("You have entered this domain: %s.\n Do you confirm this is correct? [y/n]" % domain)
		vhostfile = domain
		if confirm == 'y':
			vhostfile = nginx_hosts + '/' + vhostfile
			if os.path.isfile(vhostfile) is True:
				print "%s domain has already been added." % domain
				vhostcreate( raw_input('Please, enter domain name: ') )
			else:
				vhfile = open(vhostfile, 'w')
				vhfile.write(vhostdata(domain))
				vhfile.close()
				print ""
				update_hosts = raw_input('VHost was generated successfully!\n Do you want to add new domain to \'hosts\' file? [y/n]: ')
				if update_hosts == 'y':
					hostsfile = open('/etc/hosts', 'a')
					hostsfile.write("""127.0.0.1\t%s""" % domain)
					hostsfile.close()
				generate_home_dir = raw_input('Do you want to create folders for the website? [y/n]: ')
				if generate_home_dir == 'y':
					home_dir_html = sites_dir + '/' + domain + '/' + html_dir
					home_dir_logs = sites_dir + '/' + domain + '/' + 'logs'
					print "Website folders will be created as following: \n%s \n%s\n If there is such named directory, then the directory will not be created." % (home_dir_html,home_dir_logs)
					if not os.path.exists(home_dir_html):
						# creating http directory
						os.makedirs(home_dir_html)
						# getting user and group id
						uid = pwd.getpwnam(user).pw_uid
						gid = grp.getgrnam(user).gr_gid
						# chowning folders to user
						os.chown(sites_dir + '/' + domain, uid, gid)
						os.chown(home_dir_html, uid, gid)
						# changing http dir chmod to be able to make changes
						os.chmod(home_dir_html,0777)
					if not os.path.exists(home_dir_logs):
						uid = pwd.getpwnam(user).pw_uid
						gid = grp.getgrnam(user).gr_gid
						# creating logs directory
						os.makedirs(home_dir_logs)
						# chowning logs folder to user
						os.chown(home_dir_logs, uid, gid)
				# os.system("a2ensite %s" % domain)
				os.symlink(vhostfile, '/etc/nginx/sites-enabled/' + domain)
				os.system("systemctl restart nginx")
				print "All done! Please, take your time to check."
		else:
			vhostcreate( raw_input('Please, enter domain name: ') )
	else:
		vhostcreate( raw_input('Please, enter domain name: ') )

vhostcreate( raw_input('Please, enter domain name: ') )
