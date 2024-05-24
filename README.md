This project will allow users to input sell and buy orders into the 'market'. Once the order is received it is automatically entered into the order book which is sorted by price - time meaning that for bids the highest bids are executed first and for sell orders the lowest sells are executed first. For both bid and sell orders if there are multiple orders at the same price, the order that arrived first will be executed first. 

**Demonstration Video**

include Youtube view here 

**Running the program**

Navigate to the file (once you have either copied the code or forked the repo) and run the program from your terminal as pictured below. 

![Terminal Output](https://github.com/JoJo10Smith/Level2StockSim/blob/main/Screenshot%20from%202024-05-23%2020-48-49.png)

The following dashboard should come up in your browser. If not then you will need to click on the link in the terminal that is outputted when you run the program. 

![Running the file for the first time](https://github.com/JoJo10Smith/Level2StockSim/blob/main/Screenshot%20from%202024-05-23%2021-02-14.png)

You can put in multiple orders on both sides and the graph below will update with the cumulative bids and asks at a given price point. The graph is limited to $0 - $50 for demonstrative purposes. When an order is placed that can be executed the order book is updated as well as the graph below and a new line is entered into the ' Executed Orders' section. If an order cannot be fully executed the remaining volume is placed as an order in the order book to be executed. 

![Adding Orders to the orderbook](https://github.com/JoJo10Smith/Level2StockSim/blob/main/Screenshot%20from%202024-05-23%2021-01-48.png)

The graph will also update with the outstanding bids (buys) in red and the asks (sells) in green. Below is another example of what the output will look like - not the same orders as the images above.

![Updating Ordergraph](https://github.com/JoJo10Smith/Level2StockSim/blob/main/Screenshot%20from%202024-05-23%2021-10-57.png) 

Please feel free to leave any comments/ open an issue
