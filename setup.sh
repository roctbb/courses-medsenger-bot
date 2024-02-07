sudo pip3 install -r requirements.txt
sudo cp courses.ini /etc/uwsgi/apps/
sudo cp agents_courses.conf /etc/supervisor/conf.d/
sudo cp agents_courses_nginx.conf /etc/nginx/sites-enabled/
sudo supervisorctl update
sudo systemctl restart nginx
sudo certbot --nginx -d courses.ai.medsenger.ru
touch config.py