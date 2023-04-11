create table usuarios(
	email varchar(50) CHECK (Email LIKE '%_@__%.__%') unique not null primary key,
	nombre varchar(50) not null,
	telefono varchar(20) unique not null,
	hashed_password varchar(60) not null,
	enabled bool not null default false,
	verification_code varchar(64) not null
);

create table empresas(
	primary key (email)
) inherits (usuarios);

create table personas(
	primary key (email),
	apellido varchar(50) not null
) inherits (usuarios);