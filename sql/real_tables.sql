create table usuarios(
	id serial primary key,
	email varchar(50) CHECK (Email LIKE '%_@__%.__%') unique not null,
	nombre varchar(50) not null,
	telefono varchar(20) unique not null,
	hashed_password varchar(60),
	enabled bool not null default false
);

create table empresas(
	primary key (id)
) inherits (usuarios);

create table personas(
	primary key (id),
	apellido varchar(50) not null
) inherits (usuarios);