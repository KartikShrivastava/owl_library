# Owl Library
A minimal REST api written using django framework. This api uses django-rest-framework in REST api layer and uses postgresql in database layer.

### Class and ER diagrams
#### Current state diagram
![diagram 1](diagrams/ClassAndERDV2.png)
#### Legacy diagram
![diagram 1](diagrams/ClassAndERD.png)

### Project setup instructions
1. Create a virtual environment for the project
2. Activate virtual environment
3. Run `pip install -r requirements.txt`
4. Create a `.env` file inside `owl_library` directory
5. Put following contents in your `.env` file (update fields according to your psql configuration)  
  DATABASE_NAME=existing_psql_database_name  
  DATABASE_USER=your_psql_username  
  DATABASE_PASS=your_psql_password

## References
[Django-rest-framework docs](https://www.django-rest-framework.org/)  
[Django docs](https://docs.djangoproject.com/en/4.1/)  
[Django Web Framework (Python) tutorial](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django)  
[Django REST Framework Oversimplified](https://www.youtube.com/watch?v=cJveiktaOSQ&list=LL&index=2&ab_channel=DennisIvy)  
[Django Rest Framework | Serializers & CRUD](https://www.youtube.com/watch?v=TmsD8QExZ84&ab_channel=DennisIvy)  
[Django REST Framework - Build an API from Scratch](https://www.youtube.com/watch?v=i5JykvxUk_A&ab_channel=CalebCurry)  
