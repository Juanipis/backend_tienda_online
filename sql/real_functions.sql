-- Para insertar personas
CREATE OR REPLACE FUNCTION insert_usuario(
	varchar(100),
	varchar(50),
	varchar(10),
	varchar(60),
	bool,
	varchar(50),
	bool
) RETURNS BOOLEAN AS $$
DECLARE
  p_email varchar(100);
  p_nombre varchar(50);
  p_telefono varchar(20);
  p_hashed_password varchar(60);
  p_enabled bool;
  p_apellido varchar(50);
  p_is_persona bool;
  success BOOLEAN := FALSE;
BEGIN
  p_email := $1;
  p_nombre := $2;
  p_telefono := $3;
  p_hashed_password := $4;
  p_enabled := $5;
  p_apellido := $6;
  p_is_persona := $7;
  BEGIN
    IF not usuarioExiste(p_email) THEN
      IF p_is_persona THEN
        INSERT INTO personas(email, nombre,telefono, hashed_password, enabled, apellido)
        VALUES (p_email, p_nombre, p_telefono,p_hashed_password, p_enabled, p_apellido);
      ELSE
          INSERT INTO empresas(email, nombre, telefono, hashed_password, enabled)
          VALUES (p_email, p_nombre, p_telefono, p_hashed_password, p_enabled);
      END IF;
		success := TRUE;
	ELSE
		success := FALSE;
	END IF;
  END;
  RETURN success;
END;
$$ LANGUAGE plpgsql;

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

