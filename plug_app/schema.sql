drop table if exists user;

create table user (
	id integer primary key autoincrement,
	username varchar not null unique,
	email varchar not null unique,
	password varchar not null
);