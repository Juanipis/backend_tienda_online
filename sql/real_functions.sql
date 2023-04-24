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

CREATE OR REPLACE FUNCTION buscar_info_usuario(id integer)
RETURNS TABLE (email_t varchar(50), nombre_t varchar(50), telefono_t varchar(20), enabled_t bool, apellido_t varchar(50)) AS $$
BEGIN
  IF EXISTS (SELECT 1 FROM personas WHERE personas.id = buscar_usuario.id) THEN
    RETURN QUERY SELECT email, nombre, telefono, enabled, apellido FROM personas WHERE personas.id = buscar_usuario.id;
  ELSIF EXISTS (SELECT 1 FROM empresas WHERE empresas.id = buscar_usuario.id) THEN
    RETURN QUERY SELECT email, nombre, telefono, enabled, CAST(NULL AS varchar(50)) AS apellido FROM empresas WHERE empresas.id = buscar_usuario.id;
  ELSE
    RAISE EXCEPTION 'No se encontró el usuario con id %', buscar_usuario.id;
  END IF;
END;
$$ LANGUAGE plpgsql;