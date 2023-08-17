const promisify = require('util').promisify;
const execFile = require('child_process').execFile;
const path = require('path');
const fileURLToPath = require('url').fileURLToPath;
const express = require('express');


const app = express();
const p_execFile = promisify(execFile);


const port = 4960;
const HTTP_SERVER_ROOT = path.resolve(__dirname);
const PROJECT_ROOT = path.dirname(HTTP_SERVER_ROOT);

//Handle default form post requests
app.use(express.urlencoded({
    extended: true,
    limit: "2Mb"
})); //To populate req.body with submitted form data.


app.get('/:journal_name/quick-note/add', (req,res) => {
    res.sendFile(`${HTTP_SERVER_ROOT}/default-pages/add-quick-note.html`)
});


app.post('/:journal_name/quick-note/add', (req,res) => {
    let journal_name = req.params["journal_name"];
    // .replaceAll is only available for node.js 15.0 and after.
    let text = req.body.text.replace(/\r/g,"");
    add_quick_note(journal_name, text)
      .then( () => {
          res.redirect(`/${journal_name}`)
      })
      .catch( error => {
        res.send("Oups! An error occurred!")
      });
});


app.use('/',express.static(`${PROJECT_ROOT}/site`));


//Not able to make it work inside a container when specifying the hostname
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});


function add_quick_note(journal_name, text) {
    let BIN_DIR = path.resolve(__dirname,"./bin");
    const addQuickNotes = `${BIN_DIR}/add-quick-note/add-quick-note.sh`;

    let wd = p_execFile(addQuickNotes, [journal_name, text]);

    return wd.then(result => new Promise(function(resolve) {
        console.info("[add-quick-note][stdout]:",result.stdout);
        console.error("[add-quick-note][stderr]:",result.stderr);

        resolve(result.stdout);
    }))
    .catch( error => {
        console.log(error);
        throw error;
    });

}
