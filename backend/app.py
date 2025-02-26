from flask import Flask, request, jsonify
import pickle
import pandas as pd
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允許跨域請求


# 加載模型和處理器
with open('robust_scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('model_freq_map.pkl', 'rb') as f:
    model_freq_map = pickle.load(f)
with open('logistic_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('model_metrics.json', 'r') as f:
    metrics = json.load(f)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        category_anomaly = data.get('category_anomaly')
        Maker = data.get('Maker')
        Model = data.get('Model')
        Seat_num = data.get('Seat_num')
        Door_num = data.get('Door_num')
        repair_cost = float(data.get('repair_cost'))
        repair_hours = float(data.get('repair_hours'))
        repair_complexity = data.get('repair_complexity')

        # 驗證輸入
        if category_anomaly not in {0, 1}:
            return jsonify({'error': 'category_anomaly 需為 0 或 1'}), 400
        if not (2 <= Seat_num <= 20):
            return jsonify({'error': 'Seat_num 需在 2-20 之間'}), 400
        if not (2 <= Door_num <= 7):
            return jsonify({'error': 'Door_num 需在 2-7 之間'}), 400
        if repair_complexity not in {1, 2, 3, 4}:
            return jsonify({'error': 'repair_complexity 需為 1-4'}), 400
        # 特徵工程
        maker_dacia = 1 if Maker.lower() == 'dacia' else 0
        maker_ford = 1 if Maker.lower() == 'ford' else 0
        model_freq = model_freq_map.get(Model, min(model_freq_map.values()))

        num_features = [[model_freq, Seat_num, Door_num, repair_cost, repair_hours]]
        scaled_num = scaler.transform(num_features)

        final_features = pd.DataFrame(
            data={
                'Seat_num': scaled_num[:, 1],
                'Door_num': scaled_num[:, 2],
                'repair_cost': scaled_num[:, 3],
                'repair_hours': scaled_num[:, 4],
                'Model_FreqEncoded': scaled_num[:, 0],
                'category_anomaly': [category_anomaly],
                'Maker_Ford': [maker_ford],
                'repair_complexity': [repair_complexity],
                'Maker_Dacia': [maker_dacia]
            }
        )

        # 預測
        proba = model.predict_proba(final_features)[0][1]
        result = '會理賠' if proba > 0.5 else '不會理賠'

        return jsonify({
            'prediction': result,
            'probability': proba
        })

    except Exception as e:
        print('Exception', e)
        return jsonify({
        "error": f"预测失败：{str(e)}",
        "type": type(e).__name__,
        "debug": "请检查输入参数是否符合要求"
        }), 500


if __name__ == '__main__':
    app.run(debug=True)