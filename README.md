# flask_blog

## Introduction

A basic blog application called Flaskr

## Installation

1. Clone this repository

   ```bash
    git clone https://github.com/DevxPi/flask_blog.git
    ```

2. Create virtualenv and activate it.

   ```bash
   # linux
   python3 -m venv env
   source env/bin/activate

   #or 

   # windows
   py -m venv env
   .\env\Scripts\activate
   ```

3. run db command

   ```bash
   flask --app flaskr init-db
   ```

## Run it

```bash
flask --app flaskr run --debug
```

The application serves on `port:5000`

### Keep developing

- [x] A detail view to show a single post. Click a post’s title to go to its page.
- [x] Like / unlike a post.
- [x] Comments.
- [ ] Tags. Clicking a tag shows all the posts with that tag.
- [ ] A search box that filters the index page by name.
- [ ] Paged display. Only show 5 posts per page.
- [ ] Upload an image to go along with a post.
- [x] Format posts using Markdown.
- [ ] An RSS feed of new posts.
- [ ] Add markdown support
