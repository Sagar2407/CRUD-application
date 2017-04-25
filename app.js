var express = require('express');
var mongoose = require('mongoose');
var app = express(); // instance of express
var bodyParser = require('body-parser'); // this will help in grabing values from front end and the urls.
var Book = require('./Book.model.js');

var db = 'mongodb://localhost/example';
mongoose.connect(db);

app.use(bodyParser.json());	//telling explicitly to use body Parser to parse the json objects
app.use(bodyParser.urlencoded({		//urlencoded will help us in getting the elements from thr body elements to the url
	extended: true
}));

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
			console.log(books);		//consols to the node js console.
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

 app.post('/books', function (req,res) {		//we are posting now instead of get
	var newBook = new Book();
	newBook.title = req.body.title;
	newBook.author = req.body.author;
	newBook.category = req.body.category;

	newBook.save(function (err,book) {
		if(err){
			console.log("Some error has occured");
		}
		else{
			console.log(book);
			res.send(book);
		}
    });
});

app.post('/books2', function (req,res) {		//works the same way as the previous one.
	Book.create(req.body, function (err, book) {	//The difference being that we are not requesting element one by one.
        if(err){
            console.log("Some error has occured");
        }
        else{
            console.log(book);
            res.send(book);
        }
    });
})
var port = 8009;  // localhost:8009

app.put('/books/:id', function (req, res) {
	Book.findOneAndUpdate({
	_id: req.params.id		//This is a main query
	},
		{$set: {title: req.body.title}},	//this is a condition
		{upsert:true},					//optional parameter
		function (err,newBook) {		//callback
			if(err){
				console.log("Error occurred");
			}
			else{
				console.log(newBook);
				res.status(204);		//this will indicate that the book was updated correctly.
				// res.send(newBook)	this would also work instead of the previous line.
			}
        });
});

app.delete('/books/:id', function (req,res) {
	Book.findOneAndRemove({
		_id: req.params.id
	},function (err,book) {
		if(err){
			console.log("Error has occurred")
		}
		else{
			console.log(book)
			res.status(204)		//This line explain that the code has operation was fine,
		}
        }
	)
})

app.listen(port, function(){		//function is the call back function to show the console. Also "app.listen will start the server and start lsitening on port 8009"
	console.log("App listening on port: "+ port);
});