from flask import Flask, request,jsonify
app=Flask(__name__)
@app.route('/welcome',methods=['GET'])
def welcome():
    return jsonify(message="welcome to the api")


@app.route('/add',methods=['POST'])
def add():
    data=request.get_json()
    name=data.get('name')
    age=data.get('age')
    return jsonify(message=f"Hello {name} your age is {age}")

@app.route('/update',methods=['PUT'])
def update():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify(error="JSON payload must be a list of dictionaries"), 400
    
    responses = []
    for item in data:
        if not isinstance(item, dict):
            return jsonify(error="Each item in the list must be a dictionary"), 400
        n1 = item.get('name', 'guest')
        n2 = item.get('age', 12)
        n3 = item.get('place', 'hyd')
        responses.append(f"Hello {n1}! your data submitted successfully with age {n2} and place {n3}")
    
    return jsonify(messages=responses)

@app.route('/delete',methods=['DELETE'])
def delete():
    data=request.get_json()
    name=data.get('name')
    age=data.get('age')
    if not name or not age:
        return jsonify(error="invalid data"),400
    return jsonify(message=f"Hello {name} and {age} your data deleted successfully")
if __name__ == '__main__':
    app.run(debug=True)
