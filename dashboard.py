import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
import uuid

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create the order book with a list of the outstanding asks (sells) and bids (buys)
order_book = {
    'Buy': pd.DataFrame(columns=['Price', 'Volume', 'Time', 'OrderID']),
    'Sell': pd.DataFrame(columns=['Price', 'Volume', 'Time', 'OrderID'])
}

# Create a list of the orders that have executed 
executed_orders = pd.DataFrame(columns=['Price', 'Volume', 'BuyOrderID', 'SellOrderID', 'Time', 'OrderID'])

def generate_table(dataframe, max_rows=10):
    """ Generate the individual tables that will be used to display orders """
    return html.Table([
        html.Thead(html.Tr([html.Th(col) for col in dataframe.columns])),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col], style={'padding': '8px 12px'}) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ], style={'borderCollapse': 'collapse', 'width': '100%', 'marginBottom': '20px'})

def generate_order_graph():
    """ Add the lists of asks and bids to the plotly table """
    buy_orders = order_book['Buy'].groupby('Price').agg({'Volume': 'sum'}).sort_index(ascending=False).cumsum().reset_index()
    sell_orders = order_book['Sell'].groupby('Price').agg({'Volume': 'sum'}).sort_index().cumsum().reset_index()
    
    buy_trace = go.Bar(
        x=buy_orders['Price'],
        y=buy_orders['Volume'],
        name='Bids',
        marker=dict(color='red'),
        opacity=0.6
    )
    
    sell_trace = go.Bar(
        x=sell_orders['Price'],
        y=sell_orders['Volume'],
        name='Asks',
        marker=dict(color='green'),
        opacity=0.6
    )
    
    return {
        'data': [buy_trace, sell_trace],
        'layout': go.Layout(
            title='Order Book',
            xaxis=dict(title='Price', range=[0, 50]),
            yaxis=dict(title='Quantity'),
            barmode='overlay'
        )
    }

def generate_executed_orders_graph():
    """ Generate the line chart for executed orders """
    if executed_orders.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title='Executed Orders',
                xaxis=dict(title='Time'),
                yaxis=dict(title='Price')
            )
        }
    
    time = pd.to_datetime(executed_orders['Time'])
    price_trace = go.Scatter(
        x=time,
        y=executed_orders['Price'],
        mode='lines+markers',
        name='Price'
    )
    
    return {
        'data': [price_trace],
        'layout': go.Layout(
            title='Executed Orders',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Price')
        )
    }

def match_orders_buy():
    """ Matching algorithm for the buy orders"""
    global order_book, executed_orders
    
    buy_orders = order_book['Buy'].sort_values(by=['Price','Time'], ascending=[False, True])
    sell_orders = order_book['Sell'].sort_values(by=['Price','Time'], ascending=[True, True])
    
    i = 0
    while i < len(buy_orders):
        buy_order = buy_orders.iloc[i]
        matches = sell_orders[sell_orders['Price'] <= buy_order['Price']]
        
        if not matches.empty:
            for j in range(len(matches)):
                sell_order = matches.iloc[j]
                exec_volume = min(buy_order['Volume'], sell_order['Volume'])
                
                executed_orders = pd.concat([executed_orders, pd.DataFrame([{
                    'Price': sell_order['Price'],
                    'Volume': exec_volume,
                    'BuyOrderID': buy_order['OrderID'],
                    'SellOrderID': sell_order['OrderID'],
                    'Time': datetime.now().strftime('%H:%M:%S.%f'),
                    'OrderID': str(uuid.uuid4())[:10]
                }])], ignore_index=True)
                
                # Update volumes in the order book
                buy_order_idx = order_book['Buy'].index[order_book['Buy']['OrderID'] == buy_order['OrderID']].tolist()
                sell_order_idx = order_book['Sell'].index[order_book['Sell']['OrderID'] == sell_order['OrderID']].tolist()
                
                order_book['Buy'].at[buy_order_idx[0], 'Volume'] -= exec_volume
                order_book['Sell'].at[sell_order_idx[0], 'Volume'] -= exec_volume
                
                # Remove fully executed orders
                if order_book['Buy'].at[buy_order_idx[0], 'Volume'] == 0:
                    order_book['Buy'] = order_book['Buy'].drop(buy_order_idx)
                    break
                
                if order_book['Sell'].at[sell_order_idx[0], 'Volume'] == 0:
                    order_book['Sell'] = order_book['Sell'].drop(sell_order_idx)
                
                # Update the buy_order with the remaining volume if partially filled
                if buy_order['Volume'] > exec_volume:
                    buy_order['Volume'] -= exec_volume
                    buy_orders = buy_orders.drop(matches.index[j])
                else:
                    break
        i += 1

def match_orders_sell():
    """ Matching algorithm for the sell orders """
    global order_book, executed_orders
    
    buy_orders = order_book['Buy'].sort_values(by=['Price','Time'], ascending=[False, True])
    sell_orders = order_book['Sell'].sort_values(by=['Price','Time'], ascending=[True, True])
    
    i = 0
    while i < len(sell_orders):
        sell_order = sell_orders.iloc[i]
        matches = buy_orders[buy_orders['Price'] >= sell_order['Price']]
        
        if not matches.empty:
            for j in range(len(matches)):
                buy_order = matches.iloc[j]
                exec_volume = min(sell_order['Volume'], buy_order['Volume'])
                
                executed_orders = pd.concat([executed_orders, pd.DataFrame([{
                    'Price': buy_order['Price'],
                    'Volume': exec_volume,
                    'BuyOrderID': buy_order['OrderID'],
                    'SellOrderID': sell_order['OrderID'],
                    'Time': datetime.now().strftime('%H:%M:%S.%f'),
                    'OrderID': str(uuid.uuid4())[:10]
                }])], ignore_index=True)
                
                # Update volumes in the order book
                buy_order_idx = order_book['Buy'].index[order_book['Buy']['OrderID'] == buy_order['OrderID']].tolist()
                sell_order_idx = order_book['Sell'].index[order_book['Sell']['OrderID'] == sell_order['OrderID']].tolist()
                
                order_book['Buy'].at[buy_order_idx[0], 'Volume'] -= exec_volume
                order_book['Sell'].at[sell_order_idx[0], 'Volume'] -= exec_volume
                
                # Remove fully executed orders
                if order_book['Sell'].at[sell_order_idx[0], 'Volume'] == 0:
                    order_book['Sell'] = order_book['Sell'].drop(sell_order_idx)
                    break
                
                if order_book['Buy'].at[buy_order_idx[0], 'Volume'] == 0:
                    order_book['Buy'] = order_book['Buy'].drop(buy_order_idx)
                
                # Update the sell_order with the remaining volume if partially filled
                if sell_order['Volume'] > exec_volume:
                    sell_order['Volume'] -= exec_volume
                    sell_orders = sell_orders.drop(matches.index[j])
                else:
                    break
        i += 1

def execute_market_order(order_side, volume):
    global order_book, executed_orders
    
    if order_side == 'Buy':
        sell_orders = order_book['Sell'].sort_values(by=['Price','Time'], ascending=[True, True])
        for i in range(len(sell_orders)):
            sell_order = sell_orders.iloc[i]
            exec_volume = min(volume, sell_order['Volume'])
            
            executed_orders = pd.concat([executed_orders, pd.DataFrame([{
                'Price': sell_order['Price'],
                'Volume': exec_volume,
                'BuyOrderID': str(uuid.uuid4())[:10],
                'SellOrderID': sell_order['OrderID'],
                'Time': datetime.now().strftime('%H:%M:%S.%f'),
                'OrderID': str(uuid.uuid4())[:10]
            }])], ignore_index=True)
            
            sell_order_idx = order_book['Sell'].index[order_book['Sell']['OrderID'] == sell_order['OrderID']].tolist()
            order_book['Sell'].at[sell_order_idx[0], 'Volume'] -= exec_volume
            
            if order_book['Sell'].at[sell_order_idx[0], 'Volume'] == 0:
                order_book['Sell'] = order_book['Sell'].drop(sell_order_idx)
            
            volume -= exec_volume
            if volume == 0:
                break
    
    else:  # Sell side
        buy_orders = order_book['Buy'].sort_values(by=['Price','Time'], ascending=[False, True])
        for i in range(len(buy_orders)):
            buy_order = buy_orders.iloc[i]
            exec_volume = min(volume, buy_order['Volume'])
            
            executed_orders = pd.concat([executed_orders, pd.DataFrame([{
                'Price': buy_order['Price'],
                'Volume': exec_volume,
                'BuyOrderID': buy_order['OrderID'],
                'SellOrderID': str(uuid.uuid4())[:10],
                'Time': datetime.now().strftime('%H:%M:%S.%f'),
                'OrderID': str(uuid.uuid4())[:10]
            }])], ignore_index=True)
            
            buy_order_idx = order_book['Buy'].index[order_book['Buy']['OrderID'] == buy_order['OrderID']].tolist()
            order_book['Buy'].at[buy_order_idx[0], 'Volume'] -= exec_volume
            
            if order_book['Buy'].at[buy_order_idx[0], 'Volume'] == 0:
                order_book['Buy'] = order_book['Buy'].drop(buy_order_idx)
            
            volume -= exec_volume
            if volume == 0:
                break

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Level 2 Market Data Dashboard"),
            html.Hr(),
            html.H4("Buy Orders (outstanding)"),
            html.Div(id='buy-orders-table'),
            html.Hr(),
            html.H4("Sell Orders (outstanding)"),
            html.Div(id='sell-orders-table'),
            html.Hr(),
            html.H4("Executed Orders"),
            html.Div(id='executed-orders-table')
        ], width=6),
        dbc.Col([
            html.H4("Place Order"),
            dbc.CardGroup([
                dbc.Label("Order Side"),
                dbc.RadioItems(
                    options=[
                        {'label': 'Buy', 'value': 'Buy'},
                        {'label': 'Sell', 'value': 'Sell'}
                    ],
                    value='Buy',
                    id='order-side'
                ),
            ]),
            dbc.CardGroup([
                dbc.Label("Order Type"),
                dbc.RadioItems(
                    options=[
                        {'label': 'Market Order', 'value': 'Market'},
                        {'label': 'Limit Order', 'value': 'Limit'}
                    ],
                    value='Limit',
                    id='order-type'
                ),
            ]),
            dbc.CardGroup([
                dbc.Label("Price"),
                dbc.Input(type='number', id='order-price', value=0)
            ], id='price-input-group'),
            dbc.CardGroup([
                dbc.Label("Volume"),
                dbc.Input(type='number', id='order-volume', value=0)
            ]),
            dbc.Button("Place Order", id='place-order', color='primary')
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='order-book-graph')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='executed-orders-graph')
        ])
    ])
], fluid=True)

@app.callback(
    Output('price-input-group', 'style'),
    Input('order-type', 'value')
)
def toggle_price_input(order_type):
    if order_type == 'Market':
        return {'display': 'none'}
    return {'display': 'block'}

@app.callback(
    Output('buy-orders-table', 'children'),
    Output('sell-orders-table', 'children'),
    Output('order-book-graph', 'figure'),
    Output('executed-orders-table', 'children'),
    Output('executed-orders-graph', 'figure'),
    Input('place-order', 'n_clicks'),
    State('order-side', 'value'),
    State('order-type', 'value'),
    State('order-price', 'value'),
    State('order-volume', 'value')
)
def update_order_book(n_clicks, order_side, order_type, price, volume):
    if n_clicks:
        if order_type == 'Market':
            execute_market_order(order_side, volume)
        else:
            order_id = str(uuid.uuid4())[:10]
            current_time = datetime.now().strftime('%H:%M:%S.%f')
            
            if order_side == 'Buy':
                new_order = pd.DataFrame([[price, volume, current_time, order_id]], columns=['Price', 'Volume', 'Time', 'OrderID'])
                order_book['Buy'] = pd.concat([order_book['Buy'], new_order]).sort_values(by='Price', ascending=False).reset_index(drop=True)
                match_orders_buy()
            else:
                new_order = pd.DataFrame([[price, volume, current_time, order_id]], columns=['Price', 'Volume', 'Time', 'OrderID'])
                order_book['Sell'] = pd.concat([order_book['Sell'], new_order]).sort_values(by='Price', ascending=True).reset_index(drop=True)
                match_orders_sell()
        
    buy_orders_table = generate_table(order_book['Buy'])
    sell_orders_table = generate_table(order_book['Sell'])
    order_book_graph = generate_order_graph()
    executed_orders_table = generate_table(executed_orders)
    executed_orders_graph = generate_executed_orders_graph()
    
    return buy_orders_table, sell_orders_table, order_book_graph, executed_orders_table, executed_orders_graph

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
