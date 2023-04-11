-- Para insertar personas
CREATE OR REPLACE FUNCTION insert_persona(
	varchar(100),
  varchar(50),
  varchar(10),
	varchar(60),
	bool,
	varchar(64),
  varchar(50)
) RETURNS BOOLEAN AS $$
DECLARE
  p_email varchar(100);
  p_nombre varchar(50);
  p_telefono varchar(20);
  p_hashed_password varchar(60);
  p_enabled bool;
  p_verification_code varchar(64);
  p_apellido varchar(50);
  success BOOLEAN := FALSE;
BEGIN
  p_email := $1;
  p_nombre := $2;
  p_telefono := $3;
  p_hashed_password := $4;
  p_enabled := $5;
  p_verification_code := $6;
  p_apellido := $7;
  BEGIN
    INSERT INTO personas(email, nombre,telefono, hashed_password, enabled, verification_code, apellido)
    VALUES (p_email, p_nombre, p_telefono,p_hashed_password, p_enabled, p_verification_code, p_apellido);
    success := TRUE;
  EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'El correo electrónico ya existe en la tabla.';
    success := FALSE;
  END;
  RETURN success;
END;
$$ LANGUAGE plpgsql;
-- Para insertar empresas
CREATE OR REPLACE FUNCTION insert_empresa(
  varchar(100),
  varchar(50),
  varchar(20),
  varchar(60),
  bool,
  varchar(64)
) RETURNS BOOLEAN AS $$
DECLARE
  p_email varchar(100);
  p_nombre varchar(50);
  p_telefono varchar(20);
  p_hashed_password varchar(60);
  p_enabled bool;
  p_verification_code varchar(64);
  success BOOLEAN := FALSE;
BEGIN
  p_email := $1;
  p_nombre := $2;
  p_telefono := $3;
  p_hashed_password := $4;
  p_enabled := $5;
  p_verification_code := $6;
  BEGIN
    INSERT INTO empresas(email, nombre, telefono, hashed_password, enabled, verification_code)
    VALUES (p_email, p_nombre, p_telefono, p_hashed_password, p_enabled, p_verification_code);
    success := TRUE;
  EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'El correo electrónico ya existe en la tabla.';
    success := FALSE;
  END;
  RETURN success;
END;
$$ LANGUAGE plpgsql;

-- Para verificar token de registro
CREATE FUNCTION verificarTokenRegistro(varchar(64))
	returns boolean
AS $$
DECLARE
	token varchar(64);
	user_found boolean;
BEGIN
	token:= $1;
	 IF EXISTS(SELECT * FROM usuarios WHERE verification_code = token and enabled=false) THEN
        user_found := true;
    ELSE
        user_found := false;
    END IF;
	return user_found;
END $$ LANGUAGE plpgsql;

-- Para activar usuarios
CREATE FUNCTION activarusuario(varchar(64))
	returns boolean
AS $$
DECLARE
	token varchar(64);
BEGIN
	token:= $1;
	UPDATE usuarios SET enabled = true WHERE verification_code = token;
	return true;
END $$ LANGUAGE plpgsql;

-- Para verificar si un usuario existe
CREATE FUNCTION usuarioExiste(varchar(50))
	returns boolean
AS $$
DECLARE
	emailEnter varchar(100);
BEGIN
	emailEnter:= $1;
	IF EXISTS(SELECT email FROM usuarios WHERE email=emailEnter) THEN
		RETURN true;
	ELSE
		RETURN FALSE;
	END IF;
END $$ LANGUAGE plpgsql;

