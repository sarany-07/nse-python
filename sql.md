drop database if exists nse_sme_announcements;

create database nse_sme_announcements;

use nse_sme_announcements;

create table rawTabel(
	id int primary key not null unique auto_increment,
    annoucement_date date,
    file_url varchar(2001),
    file_text varchar(2000),
    subject varchar(500),
    file_size varchar(100),
    stock_name varchar(500),
    symbol varchar(200)
);