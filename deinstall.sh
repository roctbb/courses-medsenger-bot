sudo rm /etc/supervisor/conf.d/agents_courses.conf
sudo rm /etc/nginx/sites-enabled/agents_courses_nginx_services.conf
sudo supervisorctl update
sudo systemctl restart nginx
