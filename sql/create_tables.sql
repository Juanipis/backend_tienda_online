create table users(
	email varchar(100) CHECK (Email LIKE '%_@__%.__%') primary key,
	hashed_password varchar(60) not null
);