-- optional!
CREATE FUNCTION check_tag_count() RETURNS trigger AS $$
DECLARE n INT;
BEGIN
  SELECT COUNT(*) INTO n FROM review_tags WHERE review_id = NEW.review_id;
  IF n >= 10 THEN
    RAISE EXCEPTION 'Too many tags';
  END IF;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER check_tag_count_trigger
  BEFORE UPDATE OR INSERT ON review_tags
  FOR EACH ROW
  EXECUTE FUNCTION check_tag_count();