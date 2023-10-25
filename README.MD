Armada Assessment Test 2
----
This test is to develop REST API for student enrollment for a
department. _(Recommended Flask or FastAPI)._
You can persist data in any database of your choice.
You can send following JSON as POST, PUT, DELETE and GET requests to REST endpoints

Assumptions: Always a first name, last name, and class populated in student object.

<b>How To Run:</b>
- Open project via command line or IDE
- Install requirements from requirements.txt
- - `pip install -r requirements.txt`
- run `uvicorn main:app --reload` in terminal to start app
- To test; go to http://127.0.0.1:8000/ in browser and get Hello World output
- Utilize http://127.0.0.1:8000/docs to run samples on the fly by expanding a default path and clicking "Try it out"
- If data needed; go to http://127.0.0.1:8000/createSampleData to populate database OR click "Try it out" and execute on `createSampleData` dropdown on the /docs page
- Can run test(s) from `test_main.py` in IDE for further checks

<b>Paths to run directly:</b>
- [GET] /fetchStudents/?s_class={STUDENTS CLASS}
  - Enter a class name (Example: "A 3") to retrieve all students that are enrolled in that class
- [GET] /fetchStudents/?id={STUDENT ID}
  - Enter a student ID to retrieve said student's enrollment data
- [POST] /fetchStudents/
  - Create a student with enrollment data
  - json example for request body:
    - `{
          "firstName": "Bob",
          "lastName": "Ross",
          "student_class": "A 3",
          "nationality": "Forest"
        }`
- [PUT] /fetchStudents/{STUDENT ID}
  - Update a student via their ID. Optional choices = `firstName`, `student_class`
  - json example for request body:
  - NOTE: Both are `Optional` values
    - `{
          "firstName": "string",
          "student_class": "string"
        }`
- [DELETE] /fetchStudents/{STUDENT ID}
  - Enter a student ID to remove

<b>Requirements Checklist:</b>
- [x] Recommended: ~~Flask or~~ FastAPI
- [x] Persist data in any database of your choice. -- Using sqlite with sqlmodel
- [x] Send following JSON as POST, PUT, DELETE and GET requests to REST endpoints
- [x] Add a new record
- [x] Update an existing record on the basis of unique ID
- [x] Delete an existing record on the basis of unique ID
- [x] Fetch bulk record: all students in database for that class
- [x] Fetch student record by student id
