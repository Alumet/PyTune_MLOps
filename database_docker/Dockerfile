FROM mysql:latest

RUN cp -r /var/lib/mysql /var/lib/mysql-no-volume

CMD ["--datadir", "/var/lib/mysql-no-volume"]

ENV MYSQL_ROOT_PASSWORD pytune

EXPOSE 3306
