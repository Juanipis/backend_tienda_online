create table users(
	email varchar(100) CHECK (Email LIKE '%_@__%.__%') primary key,
	hashed_password varchar(60) not null,
	disabled bool not null default true
	verification_code varchar(6) not null
);

CREATE OR REPLACE FUNCTION insert_user(
  p_email varchar(100),
  p_hashed_password varchar(60),
  p_disabled bool DEFAULT true
	p_verification_code varchar(6)
) RETURNS BOOLEAN AS $$
DECLARE
  success BOOLEAN := FALSE;
BEGIN
  BEGIN
    INSERT INTO users (email, hashed_password, disabled, verification_code)
    VALUES (p_email, p_hashed_password, p_disabled, verification_code);
    success := TRUE;
  EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'El correo electrónico ya existe en la tabla.';
    success := FALSE;
  END;
  RETURN success;
END;
$$ LANGUAGE plpgsql;
