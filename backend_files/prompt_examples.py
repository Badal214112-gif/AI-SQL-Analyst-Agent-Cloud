WINDOW_FUNCTION_EXAMPLES = """
[TOPIC: WINDOW]

User:
Tell me top 3 brands sold by each city.

SQL:
SELECT `City`,
       `Brand`,
       total_units
FROM
(
    SELECT `City`,
           `Brand`,
           SUM(`Units Sold`) AS total_units,
           DENSE_RANK() OVER(
               PARTITION BY `City`
               ORDER BY SUM(`Units Sold`) DESC
           ) AS rnk
    FROM sales_data
    GROUP BY `City`, `Brand`
) t
WHERE rnk <= 3
ORDER BY `City`, total_units DESC;


User:
Show the highest selling brand in each city.

SQL:
SELECT `City`,
       `Brand`,
       total_units
FROM
(
    SELECT `City`,
           `Brand`,
           SUM(`Units Sold`) AS total_units,
           ROW_NUMBER() OVER(
               PARTITION BY `City`
               ORDER BY SUM(`Units Sold`) DESC
           ) AS rn
    FROM sales_data
    GROUP BY `City`, `Brand`
) t
WHERE rn = 1;


User:
Show second highest selling brand in every city.

SQL:
SELECT `City`,
       `Brand`,
       total_units
FROM
(
    SELECT `City`,
           `Brand`,
           SUM(`Units Sold`) AS total_units,
           DENSE_RANK() OVER(
               PARTITION BY `City`
               ORDER BY SUM(`Units Sold`) DESC
           ) AS rnk
    FROM sales_data
    GROUP BY `City`, `Brand`
) t
WHERE rnk = 2;


User:
Rank months based on total sales.

SQL:
SELECT `Month`,
       SUM(`Total_Sale`) AS total_sales,
       RANK() OVER(
           ORDER BY SUM(`Total_Sale`) DESC
       ) AS sales_rank
FROM sales_data
GROUP BY `Month`;


User:
Show running total of sales by date.

SQL:
SELECT `DATE`,
       SUM(`Total_Sale`) AS daily_sales,
       SUM(SUM(`Total_Sale`)) OVER(
           ORDER BY `DATE`
       ) AS running_total
FROM sales_data
GROUP BY `DATE`;


User:
Compare today's sales with previous day.

SQL:
SELECT `DATE`,
       SUM(`Total_Sale`) AS sales,
       LAG(SUM(`Total_Sale`))
       OVER(
           ORDER BY `DATE`
       ) AS previous_day_sales
FROM sales_data
GROUP BY `DATE`;


User:
Show highest rated mobile in each brand.

SQL:
SELECT `Brand`,
       `Mobile Model`,
       `Customer Ratings`
FROM
(
    SELECT *,
           ROW_NUMBER() OVER(
               PARTITION BY `Brand`
               ORDER BY `Customer Ratings` DESC
           ) AS rn
    FROM sales_data
) t
WHERE rn = 1;

"""



CTE_EXAMPLES = """
[TOPIC: CTE]

User:
Show total sales for each brand using CTE.

SQL:
WITH brand_sales AS
(
    SELECT `Brand`,
           SUM(`Total_Sale`) AS total_sales
    FROM sales_data
    GROUP BY `Brand`
)
SELECT *
FROM brand_sales;


User:
Show the brand with the highest total sales using CTE.

SQL:
WITH brand_sales AS
(
    SELECT `Brand`,
           SUM(`Total_Sale`) AS total_sales
    FROM sales_data
    GROUP BY `Brand`
)
SELECT *
FROM brand_sales
ORDER BY total_sales DESC
LIMIT 1;


User:
Find cities where total sales are above the overall average city sales.

SQL:
WITH city_sales AS
(
    SELECT `City`,
           SUM(`Total_Sale`) AS total_sales
    FROM sales_data
    GROUP BY `City`
)
SELECT *
FROM city_sales
WHERE total_sales >
(
    SELECT AVG(total_sales)
    FROM city_sales
);

"""


COMPLEX_SQL_EXAMPLES = """
[TOPIC: COMPLEX]

User:
Show brands whose total sales are above the average sales of all brands.

SQL:
SELECT `Brand`,
       SUM(`Total_Sale`) AS total_sales
FROM sales_data
GROUP BY `Brand`
HAVING SUM(`Total_Sale`) >
(
    SELECT AVG(total_sales)
    FROM
    (
        SELECT SUM(`Total_Sale`) AS total_sales
        FROM sales_data
        GROUP BY `Brand`
    ) t
);


User:
Show the top 5 cities by total revenue.

SQL:
SELECT `City`,
       SUM(`Total_Sale`) AS total_sales
FROM sales_data
GROUP BY `City`
ORDER BY total_sales DESC
LIMIT 5;


User:
Find brands that sold more units than the average units sold across all brands.

SQL:
SELECT `Brand`,
       SUM(`Units Sold`) AS total_units
FROM sales_data
GROUP BY `Brand`
HAVING SUM(`Units Sold`) >
(
    SELECT AVG(total_units)
    FROM
    (
        SELECT SUM(`Units Sold`) AS total_units
        FROM sales_data
        GROUP BY `Brand`
    ) t
);


User:
Show monthly sales growth.

SQL:
SELECT `Month`,
       SUM(`Total_Sale`) AS total_sales,
       SUM(`Total_Sale`)
       - LAG(SUM(`Total_Sale`))
         OVER(ORDER BY `Month`) AS growth
FROM sales_data
GROUP BY `Month`;


User:
Find the city contributing the highest revenue.

SQL:
SELECT `City`,
       SUM(`Total_Sale`) AS total_sales
FROM sales_data
GROUP BY `City`
ORDER BY total_sales DESC
LIMIT 1;


User:
Show average customer rating for each brand.

SQL:
SELECT `Brand`,
       ROUND(AVG(`Customer Ratings`),2) AS avg_rating
FROM sales_data
GROUP BY `Brand`
ORDER BY avg_rating DESC;

"""


BUSINESS_QUERY_EXAMPLES = """
[TOPIC: BUSINESS]

User:
Which brand generated the highest revenue?

SQL:
SELECT `Brand`,
       SUM(`Total_Sale`) AS total_revenue
FROM sales_data
GROUP BY `Brand`
ORDER BY total_revenue DESC
LIMIT 1;


User:
Which city generated the least revenue?

SQL:
SELECT `City`,
       SUM(`Total_Sale`) AS total_revenue
FROM sales_data
GROUP BY `City`
ORDER BY total_revenue ASC
LIMIT 1;


User:
Which payment method generated the highest revenue?

SQL:
SELECT `Payment Method`,
       SUM(`Total_Sale`) AS total_revenue
FROM sales_data
GROUP BY `Payment Method`
ORDER BY total_revenue DESC
LIMIT 1;


User:
Which mobile model sold the highest number of units?

SQL:
SELECT `Mobile Model`,
       SUM(`Units Sold`) AS total_units
FROM sales_data
GROUP BY `Mobile Model`
ORDER BY total_units DESC
LIMIT 1;


User:
Show revenue contribution of each brand.

SQL:
SELECT `Brand`,
       SUM(`Total_Sale`) AS revenue,
       ROUND(
           SUM(`Total_Sale`) * 100 /
           SUM(SUM(`Total_Sale`)) OVER(),
           2
       ) AS revenue_percentage
FROM sales_data
GROUP BY `Brand`
ORDER BY revenue DESC;


User:
Which month had the highest sales?

SQL:
SELECT `Month`,
       SUM(`Total_Sale`) AS total_sales
FROM sales_data
GROUP BY `Month`
ORDER BY total_sales DESC
LIMIT 1;


User:
Show the average selling price of each brand.

SQL:
SELECT `Brand`,
       ROUND(AVG(`Price Per Unit`),2) AS average_price
FROM sales_data
GROUP BY `Brand`
ORDER BY average_price DESC;


User:
Which city sold the maximum number of units?

SQL:
SELECT `City`,
       SUM(`Units Sold`) AS total_units
FROM sales_data
GROUP BY `City`
ORDER BY total_units DESC
LIMIT 1;


User:
Show total revenue generated by each payment method.

SQL:
SELECT `Payment Method`,
       SUM(`Total_Sale`) AS total_revenue
FROM sales_data
GROUP BY `Payment Method`
ORDER BY total_revenue DESC;


User:
Which brand has the highest average customer rating?

SQL:
SELECT `Brand`,
       ROUND(AVG(`Customer Ratings`),2) AS avg_rating
FROM sales_data
GROUP BY `Brand`
ORDER BY avg_rating DESC
LIMIT 1;

"""