/* =========================================================
   1) Tabla libraries
   ========================================================= */

CREATE TABLE IF NOT EXISTS libraries (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_libraries_code (code),
  UNIQUE KEY uq_libraries_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


/* Seed inicial */
INSERT INTO libraries (code, name)
VALUES
  ('melendo_iglesias', 'Melendo-Iglesias'),
  ('iglesias_hurtado', 'Iglesias-Hurtado')
ON DUPLICATE KEY UPDATE name = VALUES(name);


/* Biblioteca por defecto para datos actuales */
SET @DEFAULT_LIBRARY_ID := (
  SELECT id FROM libraries WHERE code = 'melendo_iglesias' LIMIT 1
);


/* =========================================================
   2) Añadir library_id a tablas necesarias (Opción C)
   - Añade índice temporal antes del UPDATE para evitar 1175
   - Actualiza con WHERE library_id IS NULL (ya indexado) o WHERE id IS NOT NULL
   ========================================================= */


/* ---------- collections ---------- */
ALTER TABLE collections
  ADD COLUMN library_id INT UNSIGNED NULL AFTER id;

-- índice temporal (para Safe Update Mode)
ALTER TABLE collections
  ADD INDEX idx_tmp_collections_library_id (library_id);

UPDATE collections
  SET library_id = @DEFAULT_LIBRARY_ID
  WHERE library_id IS NULL;

ALTER TABLE collections
  -- quitamos índice temporal
  DROP INDEX idx_tmp_collections_library_id,
  -- y dejamos la columna cerrada + índice definitivo + FK
  MODIFY COLUMN library_id INT UNSIGNED NOT NULL,
  ADD INDEX idx_collections_library_id (library_id),
  ADD CONSTRAINT fk_collections_library
    FOREIGN KEY (library_id) REFERENCES libraries(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;


/* ---------- locations ---------- */
ALTER TABLE locations
  ADD COLUMN library_id INT UNSIGNED NULL AFTER id;

ALTER TABLE locations
  ADD INDEX idx_tmp_locations_library_id (library_id);

UPDATE locations
  SET library_id = @DEFAULT_LIBRARY_ID
  WHERE library_id IS NULL;

ALTER TABLE locations
  DROP INDEX idx_tmp_locations_library_id,
  MODIFY COLUMN library_id INT UNSIGNED NOT NULL,
  ADD INDEX idx_locations_library_id (library_id),
  ADD CONSTRAINT fk_locations_library
    FOREIGN KEY (library_id) REFERENCES libraries(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;


/* ---------- books (la clave) ---------- */
ALTER TABLE books
  ADD COLUMN library_id INT UNSIGNED NULL AFTER id;

ALTER TABLE books
  ADD INDEX idx_tmp_books_library_id (library_id);

UPDATE books
  SET library_id = @DEFAULT_LIBRARY_ID
  WHERE library_id IS NULL;

ALTER TABLE books
  DROP INDEX idx_tmp_books_library_id,
  MODIFY COLUMN library_id INT UNSIGNED NOT NULL,
  ADD INDEX idx_books_library_id (library_id),
  ADD CONSTRAINT fk_books_library
    FOREIGN KEY (library_id) REFERENCES libraries(id)
    ON UPDATE CASCADE ON DELETE RESTRICT;
