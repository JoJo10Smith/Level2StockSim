This project will allow users to input sell and buy orders into the 'market'. Once the order is received it is automatically entered into the order book which is sorted by price - time meaning that for bids the highest bids are executed first and for sell orders the lowest sells are executed first. For both bid and sell orders if there are multiple orders at the same price, the order that arrived first will be executed first. 

**Demonstration Video**
include Youtube view here 

**Running the program**
Navigate to the file (once you have either copied the code or forked the repo) and run the program from your terminal as pictured below. 

%insert image here%

The following dashboard should come up in your browser. If not then you will need to click on the link in the terminal that is outputted when you run the program. 

%% insert image here 

You can put in multiple orders on both sides and that graph below will update with the cumulative bids and asks at a given price point. The graph is limited to $0 - $50 for demonstrative purposes. When are order is placed that can be executed the order book is updated as well as the graph below and a new line is entered into the ' Executed Orders' section. If an order cannot be fully executed the remaining volumn is placed as an order in the order book to be executed. 

Please feel free to leave any comments/ open an issue
