/**************Primera entrada en un dia********************/
SELECT * FROM registro WHERE fecha_hora_entrada::DATE BETWEEN '2017-03-10'::DATE AND '2017-03-10'::DATE ORDER BY fecha_hora_entrada ASC LIMIT 1;
SELECT * FROM registro ORDER BY fecha_hora_entrada ASC LIMIT 1 ;

/**************Ultima salida en un dia**********************/
SELECT * FROM registro WHERE fecha_hora_salida::DATE BETWEEN '2017-03-10'::DATE AND '2017-03-10'::DATE ORDER BY fecha_hora_salida DESC LIMIT 1;
SELECT * FROM registro ORDER BY fecha_hora_salida DESC LIMIT 1 ;

/**************Tiempo por tipo de usuario******************/
DROP VIEW IF EXISTS vista1; /*elimina vista si existe*/
CREATE VIEW vista1 AS /*crea vista*/

SELECT ID,AGE(fecha_hora_salida,fecha_hora_entrada) AS diferencia FROM registro WHERE id_usuario IN  /*Age da la diferencia entre timestamps*/
(SELECT id_usuario FROM roles_usuarios WHERE id_rol IN/*subsonsulta para separar por tipo de usuario*/
(SELECT id FROM rol WHERE name = 'admin'));
SELECT AVG(diferencia) FROM vista1; /*obtiene el promedio de tiempo*/

/**************Registros por día - semana - mes****************************/
SELECT COUNT(*) AS cantidad FROM registro WHERE fecha_hora_entrada::DATE BETWEEN '2017-03-10'::DATE AND '2017-03-10'::DATE;

/*************Computadoras por día - semana - mes**************************/
SELECT COUNT(*) from detalle_registro WHERE fecha_hora_toma::DATE BETWEEN '2017-03-10'::DATE AND '2017-03-10'::DATE;
