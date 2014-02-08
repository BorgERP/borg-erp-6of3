
CREATE OR REPLACE FUNCTION 
    oe_currency_compute( from_currency integer,
                          to_currency integer,
                          from_amount numeric,
                          company integer,
                          for_date date DEFAULT current_date,
                          update_service int DEFAULT NULL,
                          
                          round boolean DEFAULT True,
                          force_currency_rate numeric DEFAULT NULL,
                          force_currency_inv_rate numeric DEFAULT NULL,
                          from_currency_type integer DEFAULT NULL,
                          to_currency_type integer DEFAULT NULL
                       ) 
    RETURNS numeric AS
$BODY$
DECLARE
   company_currency integer;
   from_rate numeric:=0.0;
   to_rate   numeric:=0.0;
BEGIN
    IF from_currency = to_currency THEN
       RETURN from_amount;
    END IF;    
    for_date:=coalesce(for_date, current_date);  
    update_service:=coalesce(update_service,
                        (SELECT us.id FROM res_currency_rate_update_service us
                          WHERE us.company_id = company));
    from_currency_type:=coalesce( from_currency_type
                                 ,(SELECT id FROM res_currency_rate_type
                                    WHERE code='middle_rate' )
                                );
    to_currency_type:=coalesce( to_currency_type, from_currency_type); -- NOT IMPLEMENTED!
    company_currency:=(SELECT currency_id FROM res_company WHERE id = company);
    to_rate:=( SELECT cr.rate FROM res_currency_rate cr  
                WHERE name <= for_date
	          AND cr.currency_id           = to_currency
                  AND cr.currency_rate_type_id = to_currency_type
                  AND cr.update_service_id = update_service
                ORDER BY name desc, cr.update_service_id NULLS LAST LIMIT 1
             );
    from_rate:=( SELECT cr.rate FROM res_currency_rate cr  
                WHERE name <= for_date
	          AND cr.currency_id           = from_currency
                  AND cr.currency_rate_type_id = from_currency_type
                  AND cr.update_service_id = update_service
                ORDER BY name desc, cr.update_service_id NULLS LAST LIMIT 1
             );
    RETURN round( from_amount * to_rate / from_rate::numeric, 2);
END$BODY$
LANGUAGE plpgsql;

DO $$
BEGIN

IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'res_currency_rate_perf_index') 
   THEN CREATE INDEX res_currency_rate_perf_index ON res_currency_rate
                       (name DESC, update_service_id, currency_id, currency_rate_type_id);
END IF;

END$$;