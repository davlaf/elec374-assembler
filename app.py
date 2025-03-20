from flask import Flask, render_template, request
import SRC_ASM


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assemble', methods=['POST'])
def assemble_code():
    code = request.form['code']
    format_type = request.form['format']

    if format_type not in ['mem', 'mif']:
        return {"error": "invalid format"}
    
    try:
        _, output_assembly = SRC_ASM.assembly_to_file(format_type, code)
    except Exception as e:
        return {"error": str(e)}

    return {'output': output_assembly}

if __name__ == '__main__':
    app.run(debug=True)
