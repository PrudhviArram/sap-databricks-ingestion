import csv, json, os, random, string
from datetime import datetime, timedelta

def random_id(prefix, length=8):
    return prefix + ''.join(random.choices(string.digits, k=length))

def random_date(days_back=365):
    d = (datetime.now() - timedelta(days=random.randint(0, days_back))).strftime('%Y-%m-%d')
    return d

MATERIALS = ['RAW-STEEL', 'PLASTIC', 'WOOD', 'ALUMINUM', 'COPPER']
PLANTS = ['PLANT-A', 'PLANT-B', 'PLANT-C']
CUSTOMERS = [f'CUST{str(i).zfill(5)}' for i in range(1, 101)]
CURRENCIES = ['USD', 'EUR', 'INR', 'GBP', 'AUD']
STATUS = ['OPEN', 'DELIVERED', 'CANCELLED', 'PENDING']

def make_sales_orders(num_orders=1000):
    orders = []
    for _ in range(num_orders):
        order = {
            'order_id': random_id('SO'),
            'customer_id': random.choice(CUSTOMERS),
            'material': random.choice(MATERIALS),
            'quantity': random.randint(1, 100),
            'plant': random.choice(PLANTS),
            'order_date': random_date(),
            'delivery_date': random_date(),
            'currency': random.choice(CURRENCIES),
            'price_per_unit': round(random.uniform(10, 1000), 2),
            'status': random.choice(STATUS)
        }
        orders.append(order)
    return orders

def make_materials(num_materials=100):
    materials = []
    for _ in range(num_materials):
        material = {
            'material_id': random_id('MAT'),
            'description': random.choice(MATERIALS) + ' Material',
            'plant': random.choice(PLANTS),
            'stock_quantity': random.randint(0, 1000),
            'unit_of_measure': 'KG',
            'price_per_unit': round(random.uniform(10, 1000), 2)
        }
        materials.append(material)
    return materials

def make_financials(num_records=1000):
    financials = []
    for _ in range(num_records):
        record = {
            'record_id': random_id('FIN'),
            'customer_id': random.choice(CUSTOMERS),
            'amount': round(random.uniform(100, 10000), 2),
            'currency': random.choice(CURRENCIES),
            'transaction_date': random_date(),
            'payment_status': random.choice(STATUS)
        }
        financials.append(record)
    return financials

def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def write_delimiter(data, filename, delimiter=','):
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=delimiter)
        writer.writeheader()
        writer.writerows(data)

def main(base_dir='./data'):
    date_folder = datetime.now().strftime('%Y%m%d')
    output_dir = os.path.join(base_dir, date_folder)
    os.makedirs(output_dir, exist_ok=True)

    jobs = {
        'sales_orders': (make_sales_orders(), ['json', 'csv', 'tsv ']),
        'materials': (make_materials(), ['json', 'csv', 'tsv']),
        'financials': (make_financials(), ['json', 'csv', 'tsv']),
        }

    for job_name, (data, formats) in jobs.items():
        for fmt in formats:
            path = os.path.join(output_dir, f'{job_name}.{fmt}')
            if fmt == 'json':
                write_json(data, path)
            elif fmt == 'csv':
                write_delimiter(data, path, delimiter=',')
            elif fmt == 'tsv':
                write_delimiter(data, path, delimiter='\t')
            print(f'Generated {len(data)} records for {job_name} in {fmt} format at {path}')
    print('Data generation completed.')

if __name__ == '__main__':
    main()

