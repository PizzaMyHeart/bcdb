# bcdb

## Database schema

### Post
#### post_id (PK)
#### title
#### post_date
#### crawled_date
#### permalink
#### guardian_short_url
#### num_comments


### Tag
#### tag_name (PK)

### PostTag
#### post_tag_id (PK)
#### tag_name (FK)
#### post_id (FK)

### Comment
#### comment_id (PK)
#### body
#### comment_date
#### permalink
#### upvotes
#### user_id (FK)
#### post_id (FK)


### User
#### user_id (PK)
