# CAMT SE Senior Project <img align="left" width="80" height="80" src="https://scontent.fbkk12-4.fna.fbcdn.net/v/t39.30808-6/431325518_800579332108285_62558907469796459_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=5f2048&_nc_eui2=AeEogoPfZBc9n9qsGk60U-rHuJagYPsOrQq4lqBg-w6tClgDnvKtSzaRiPnL1tjo99ydIeUKTgHbPSxYGCP5G6wg&_nc_ohc=_OAHiDb5KjcQ7kNvgGzPfoW&_nc_ht=scontent.fbkk12-4.fna&oh=00_AYDkQUBLecu5pMOZvC0L4Rl4rgLMXOmH9GgNfMqihE_MFA&oe=665BD233" alt="CAMT icon">
  This is a backend for web application call "ApartEase", this application is a micromanagement for apartment management, and with OCR Mechine Learning to help aparment manager/owner/operator extract number out of electric meter and upload the data to database for convenient of those people to manage apartment.

## Feature
- Authentication
  - Login ```@app.route('/login', methods=['POST'])``` 🔐 <br>
    > JSON body `"username:str", "password:str"`
> user has to login fisrt in order to use these router list below
- CRUD for resident information database
  - Add resident ```('/resident/add', methods=['POST'])``` ✏️ <br>
    > JSON body `"name:str", "lineID:str", "roomNumber:str"`
  - Get resident list ```('/resident/list', methods=['GET'])``` 🗒️ <br>
    > JSON body `none`
  - Get resident by id ```('/resident/list/<res_id>', methods=['GET'])``` 👱🏻‍♂️ <br>
    > JSON body `none`
  - Get resident by room ```('/resident/list/room?query=<room_number>&page=<page_number>', methods=['GET'])``` 🚪 <br>
    > JSON body `none`
  - Get resident by name ```('/resident/list/name?query=<name>&page=<page_number>', methods=['GET'])``` 🎩 <br>
    > JSON body `none`
  - Update resident by id ```('/resident/edit/<res_id>', methods=['PUT'])``` ✍️ <br>
    > JSON body `"name:str", "lineId:str", "roomNumber:str"`
  - Delete resident by id ```('/resident/del/<res_id>', methods=['DELETE'])``` 💥 <br>
    > JSON body `none`
- CRUD for electric unit record database
  - Add unit record ```('/unit/add', methods=['POST'])``` ✏️ <br>
    > JSON body `"numberOfUnits:str", "extractionStatus:str", "res_room:str"`
  - GET unit record list ```('/unit/list', methods=['GET'])``` 🗒️ <br>
    > JSON body `none`
  - GET unit record by id ```('/unit/list/<uid>', methods=['GET'])``` 📃 <br>
    > JSON body `none`
  - GET unit record by date ```('/unit/list/date?start=<start_date>&end=<end_date>&page=<page_number>', methods=['GET'])``` 📆 <br>
    > JSON body `none` <br> Date format is `YYYY-mm-dd`
  - GET unit record by room number ```('/unit/list/room?query=<room_number>&page=<page_number>', methods=['GET'])``` 🚪 <br>
    > JSON body `none`
  - Update unit record by id ```('/unit/edit/<rec_id>', methods=['PUT'])``` ✍️ <br>
    > JSON body `"numberOfUnits:str", "date:str", "extractionStatus:str", "approveStatus:bool", "res_room:str"`<br> Date format is `YYYY-mm-dd`
  - Delete unit record by id ```('/unit/del/<rec_id>', methods=['DELETE'])``` 💥 <br>
    > JSON body `none`
- CRUD for user information database
  > required "Admin" role to access
  - Add user ```('/user/add', methods=['POST'])``` ✏️ <br>
    > JSON body `"username:str", "password:str", "role:str"`
  - GET user list ```('/user/list', methods=['GET'])``` 🗒️ <br>
    > JSON body `none`
  - GET user by id ```('/user/list/<uid>', methods=['GET'])``` 👨‍💻 <br>
    > JSON body `none`
  - Update user by id ```('/user/edit/<uid>', methods=['PUT'])``` ✍️ <br>
    > JSON body `"username:str", "password:str", "role:str"`
  - Delete user by id ```('/user/del/<uid>', methods=['DELETE'])``` 💥 <br>
    > JSON body `none`
- CRUD for role database
  > required "Admin" role to access
  - Add role ```('/role/add', methods=['POST'])``` ✏️ <br>
    > JSON body `"role_name:str"`
  - GET role list ```('/role/list', methods=['GET'])``` 🗒️ <br>
    > JSON body `none`
  - GET role by id ```('/role/list/<rid>', methods=['GET'])``` 🗒️ <br>
    > JSON body `none`
  - Update role by id ```('/role/edit/<rid>', methods=['PUT'])``` ✍️ <br>
    > JSON body `"role_name:str"`
  - Delete role by id ```('/role/del/<rid>', methods=['DELETE'])``` 💥 <br>
    > JSON body `none`

## Setup

1. Clone the repo.
2. Set up postgresql database on your local computer.
3. change connection port in `config.py` file to connect to your postgresql database
4. setup a virtualenv `pipenv shell`
5. install dependencies `pipenv install`

## Running the application

> type: `python run.py`
> serving on: `https://127.0.0.1:1234/`

## Credit of code template https://github.com/CIRCLECI-GWP/authentication-decorators-in-flask.git
