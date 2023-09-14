import sqlite3

conn = sqlite3.connect('Dinerdanny.db')
print("Database created and succesfully connected to Sqlite")

curr = conn.cursor()

curr.execute("""CREATE TABLE IF NOT EXISTS sales
               (
               customer_id VARCHAR(1), 
               order_date DATE,
               product_id integer
               ); """
            )

print('Table sales created.')

curr.execute("""INSERT INTO sales
                ("customer_id", "order_date", "product_id")
            VALUES
                ('A', '2021-01-01', '1'),
                ('A', '2021-01-01', '2'),
                ('A', '2021-01-07', '2'),
                ('A', '2021-01-10', '3'),
                ('A', '2021-01-11', '3'),
                ('A', '2021-01-11', '3'),
                ('B', '2021-01-01', '2'),
                ('B', '2021-01-02', '2'),
                ('B', '2021-01-04', '1'),
                ('B', '2021-01-11', '1'),
                ('B', '2021-01-16', '3'),
                ('B', '2021-02-01', '3'),
                ('C', '2021-01-01', '3'),
                ('C', '2021-01-01', '3'),
                ('C', '2021-01-07', '3');
            """)
print('Inserted values into sales table successfully.')

curr.execute("""CREATE TABLE IF NOT EXISTS menu
                (
                product_id integer, 
                product_name VARCHAR(5),
                price integer
                ); """ 
            )
print('Table menu created.')

curr.execute("""INSERT INTO menu
                    ("product_id", "product_name", "price")
               VALUES
                    ('1', 'sushi', '10'),
                    ('2', 'curry', '15'),
                    ('3', 'ramen', '12');
            """
            )
print('Inserted values into menu table successfully.')


curr.execute("""CREATE TABLE IF NOT EXISTS members
                (
                customer_id varchar(1),
                join_date DATE
                ); """
            )
print('Table members created.')

curr.execute('''INSERT INTO members
                    (customer_id, join_date)
                VALUES
                    ('A', '2021-01-07'),
                    ('B', '2021-01-09');
            ''')
print('Inserted values into members table successfully.')
conn.commit()
    

#Q1. What is the total amount each customer spent at the restaurant?

'''
    SELECT SUM(price)
    FROM sales a
    INNER JOIN menu b 
    ON a.product_id = b.product_id
    GROUP BY a.customer_id
'''

#Q2. How many days has each customer visited the restaurant?

'''
        select count(distinct(order_date)) days_visited
        FROM sales
        GROUP BY customer_id
'''

#Q3. What was the first item from the menu purchased by each customer?

'''
    SELECT a.customer_id, b.price 
    FROM 
        (
        SELECT 
        ROW_NUMBER() OVER (PARTITION BY customer_id ) as row_num,
        product_id,
        customer_id
        FROM sales) a
    JOIN menu b 
    ON a.product_id = b.product_id
    WHERE row_num = 1;
'''

#Q4. What is the most purchased item on the menu and how many times was it purchased by all customers?

'''
    SELECT count(*) num, b.product_name
    FROM sales a 
    JOIN menu b 
    ON a.product_id = b.product_id
    GROUP BY a.product_id
    ORDER BY num DESC
    LIMIT 1;
'''

#Q5. Which item was the most popular for each customer?

'''
    SELECT customer_id, b.product_name
    FROM
        (
            SELECT customer_id, 
                    product_id, 
                    count(product_id) count,
                    RANK() OVER (PARTITION BY customer_id ORDER BY count(product_id) DESC) rank
            FROM sales
            GROUP BY customer_id, product_id
        ) a
    JOIN menu b 
    ON a.product_id = b.product_id
    WHERE rank = 1
    ORDER BY customer_id
'''

#Q6. Which item was purchased first by the customer after they became a member?
# note: If the day of joining does not count, then the code will be order_date > join_date

'''
    SELECT a.customer_id, b.product_name
    FROM(
        SELECT s.customer_id, 
            join_date,
            order_date,
            product_id,
            DENSE_RANK() OVER (PARTITION BY s.customer_id ORDER BY order_date) rank
        FROM SALES s
        JOIN members m 
        ON s.customer_id = m.customer_id
        WHERE order_date >= join_date ) a 
    JOIN menu b 
    ON a.product_id = b.product_id 
    WHERE rank = 1
    ORDER BY customer_id;
'''

#Q7. Which item was purchased just before the customer became a member?

'''
    SELECT r.customer_id, product_name
    FROM (	
            select a.customer_id, 
                    order_date,
                    product_id, 
                    join_date,
                    RANK() OVER (PARTITION BY a.customer_id ORDER BY order_date DESC) rank
            from sales a	
            JOIN members b 
            ON a.customer_id = b.customer_id
            WHERE order_date < join_date) r
    JOIN menu m 
    ON r.product_id = m.product_id
    WHERE rank = 1;
'''

#Q8. What is the total items and amount spent for each member before they became a member?

'''
    SELECT r.customer_id, 
            count(r.product_id) products, 
            sum(price) total_amount
    FROM(
        SELECT a.customer_id, 
                order_date,
                product_id, 
                join_date,
                RANK() OVER (PARTITION BY a.customer_id ORDER BY order_date DESC) rank
        FROM sales a	
        JOIN members b 
        ON a.customer_id = b.customer_id
        WHERE order_date < join_date) r
    JOIN menu m 
    ON r.product_id = m.product_id
    GROUP BY r.customer_id
'''

#Q9. If each $1 spent equates to 10 points and sushi has a 2x points multiplier - how many points would each customer have?

'''
    SELECT b.customer_id, sum(points) points
    FROM
        (
        Select price, product_id,
        CASE 
            WHEN product_id = 1 THEN price * 20
            ELSE price*10
            END AS points
        FROM menu) a
    JOIN sales b
    ON a.product_id = b.product_id 
    GROUP BY b.customer_id;
'''

#Q10. In the first week after a customer joins the program (including their join date) they earn 2x points on all items, 
# not just sushi - how many points do customer A and B have at the end of January?

'''
    Select
        s.customer_id,
        Sum(CASE
                When (DATEDIFF(DAY, me.join_date, s.order_date) between 0 and 7) or (m.product_ID = 1) Then m.price * 20
                Else m.price * 10
            END) As Points
    From members as me
    Inner Join sales as s on s.customer_id = me.customer_id
    Inner Join menu as m on m.product_id = s.product_id
    where s.order_date >= me.join_date 
    Group by s.customer_id
'''





