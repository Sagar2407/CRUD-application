var express = require('express');
var mongoose = require('mongoose');
var app = express(); // instance of express
var bodyParser = require('body-parser'); // this will help in grabing values from front end and the urls.
var Book = require('./Book.model.js');

var db = 'mongodb://localhost/example';
mongoose.connect(db);

app.get('/', function(req, res){  // get method is a property of express framework and the other function is a callback.
	res.send('Hello World');		// Hello World on the localhost:8009.
})

app.get('/books', function(req,res){		// '/books' is a router which we get through localhost:8009/books
	console.log('Books listing');
	Book.find()
	.exec(function (err, books){		// Callback function  // .exec function will always be there in every query statement
		if(err){					// Checks if there is an error or not
			res.send('Error has occured');
		}
		else{
			//console.log(books);		//consols to the node js console.
			res.json(books);	// json parsing of the objects
		}
	})
})

app.get('/books/:id',function(req,res){		//Code to find just one book  Look how id is written 
	console.log('Getting only one Book');	//localhost:8009/books/<Copy paste the id> then you will get one one book
	Book.findOne({
		_id: req.params.id
			})			// Here we make request from the brwoser to fetch the id via bodyparser.
	.exec(function(err, book){
		if(err){
			res.send('Error has occured');
		}
		else{
		console.log(book);
		res.json(book);
	}
	})
})


var port = 8009;  // localhost:8009

app.listen(port, function(){		//function is the call back function to show the console. Also "app.listen will start the server and start lsitening on port 8009"
	console.log("App listening on port: "+ port);
});