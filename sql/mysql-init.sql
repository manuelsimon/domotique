UPDATE mysql.user SET Password=PASSWORD('raspberry') WHERE User='root';
GRANT ALL ON *.* to root@'192.168.1.77' IDENTIFIED BY 'raspberry';
GRANT ALL ON *.* to root@'localhost' IDENTIFIED BY 'raspberry';
FLUSH PRIVILEGES;
