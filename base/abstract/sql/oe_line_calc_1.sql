DROP FUNCTION IF EXISTS oe_line_calc_1(numeric,numeric,numeric,numeric,numeric,numeric,character varying, integer, integer, numeric, date);
CREATE OR REPLACE FUNCTION oe_line_calc_1(
	   price_unit numeric DEFAULT 0.0::numeric
	  ,quantity numeric DEFAULT 0.0::numeric
	  ,discount1_percent numeric DEFAULT 0.0::numeric
	  ,discount2_percent numeric DEFAULT 0.0::numeric
	  ,global_discount_percent numeric DEFAULT 0.0::numeric
	  ,discount_amount numeric DEFAULT 0.0::numeric
	  ,calc_type varchar DEFAULT 'wholesale'
	  ,currency_id integer DEFAULT NULL
	  ,company_id integer DEFAULT NULL
	  ,force_currency_rate numeric DEFAULT NULL
	  ,currency_date date DEFAULT NULL
)
  RETURNS 
   TABLE (
          r_price_unit numeric, r_quantity numeric
	 ,r_discount1_percent numeric, r_discount2_percent numeric, r_global_discount_percent numeric, r_discount_amount numeric
	 ,r_discount numeric, r_discount_total numeric
	 ,r_base_price numeric, r_list_amount numeric, r_amount numeric
	 ,r_ccurrency_price_subtotal numeric
	 ,r_ccurrency_base_price numeric
	 ,r_ccurrency_amount numeric
	 --,r_ccurrency_amount_tax numeric --TODO
	 ,r_supplier_cost numeric
	 --,r_total_costs numeric
	 --,r_margin_brutto1 numeric
	 --,r_margin_brutto1_percent numeric
	 --,r_margin_brutto2 numeric
	 --,r_margin_brutto2_percent numeric
)

  AS
$BODY$
DECLARE
    discount numeric;
    base_price numeric;
    list_amount numeric;
    amount numeric;
    discount_total numeric;
    ccurrency_price_subtotal numeric;
    ccurrency_base_price numeric;
    ccurrency_amount numeric;
    --ccurrency_amount_tax numeric;
    supplier_cost numeric;
    --total_costs numeric;
    --margin_brutto1 numeric;
    --margin_brutto1_percent numeric;
    --margin_brutto2 numeric;
    --margin_brutto2_percent numeric;

    company_currency integer;
    
BEGIN
    discount1_percent = coalesce(discount1_percent, 0.0);
    discount2_percent = coalesce(discount2_percent, 0.0);
    global_discount_percent = coalesce(global_discount_percent, 0.0);
    discount_amount = coalesce(discount_amount, 0.0);
    price_unit = coalesce(price_unit, 0.0);
    quantity = coalesce(quantity, 0.0);

    discount = 100 - ((100.00 - discount1_percent) * 
		      (100.00 - discount2_percent) * 
		      (100.00 - global_discount_percent) / 10000) ;
    discount = round(discount,2);
    list_amount = round(price_unit * quantity,2);
    amount = round((list_amount * (1-(discount)/100.0)) - discount_amount ,2);
    discount_total = list_amount - amount;
    base_price = CASE when abs(quantity) > 0.0 then round(amount/quantity,2)
                      else 0.0 END;

    IF (currency_id IS NOT NULL) AND (company_id IS NOT NULL) THEN
        SELECT rc.currency_id INTO company_currency FROM res_company rc WHERE rc.id = company_id; 
        ccurrency_price_subtotal = oe_currency_compute(from_currency:=currency_id, to_currency:=company_currency
                                      ,from_amount  := amount
                                      ,company:=company_id, for_date:= coalesce(currency_date, now())::date );
        ccurrency_base_price = oe_currency_compute(from_currency:=currency_id, to_currency:=company_currency
                                      ,from_amount  := base_price
                                      ,company:=company_id, for_date:= coalesce(currency_date, now())::date );
        ccurrency_amount = oe_currency_compute(from_currency:=currency_id, to_currency:=company_currency
                                      ,from_amount  := amount
                                      ,company:=company_id, for_date:= coalesce(currency_date, now())::date );
        supplier_cost = ccurrency_amount; -- For IN documents, for OUT it is calculated FIFO/LIFO
    END IF;
RETURN QUERY 
   SELECT price_unit,quantity, discount1_percent, discount2_percent, global_discount_percent, discount_amount
         ,discount, discount_total
         ,base_price, list_amount, amount
         ,ccurrency_price_subtotal 
	     ,ccurrency_base_price 
	     ,ccurrency_amount 
	     --,0. r_ccurrency_amount_tax  --TODO
	     ,supplier_cost 
	     --,0. r_total_costs --NEEDS other costs
	     --,0. r_margin_brutto1 
	     --,0. r_margin_brutto1_percent 
	     --,0. r_margin_brutto2 
	     --,0. r_margin_brutto2_percent 
    ;
END$BODY$
  LANGUAGE plpgsql VOLATILE;