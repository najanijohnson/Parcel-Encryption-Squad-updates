const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public')); // serve your HTML file

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/websiteLayout.html');
  });
  

app.post('/register', (req, res) => {
  const userData = {
    name: req.body.name,
    address: req.body.address,
    location: req.body.location,
    status: "In Transit" 
  };

  fs.appendFile('users.txt', JSON.stringify(userData) + '\n', (err) => {
    if (err) {
      res.send('Error saving data');
    } else {
        res.redirect('/');
    }
  });
});

app.get('/packages', (req, res) => {
  fs.readFile('users.txt', 'utf8', (err, data) => {
    if (err) return res.status(500).json({ error: 'Could not read file' });

    const lines = data.trim().split('\n');
    const packages = lines.map(line => JSON.parse(line));
    res.json(packages);
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});

