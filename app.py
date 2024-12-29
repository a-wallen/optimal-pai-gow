from flask import Flask, request, jsonify
import itertools
import sys
from treys import Evaluator, Card
from bisect import bisect_left

app = Flask(__name__)

def parse_cards(card_input):
    try:
        cards = [Card.new(card.strip()) for card in card_input.split()]
        if len(cards) != 13:
            raise ValueError("Exactly 13 cards are required.")
        return cards
    except Exception as e:
        return str(e)

def make_hand(cards, n):
    evaluator = Evaluator()
    best_rank = float("inf")
    best_hand = None

    for combination in itertools.combinations(cards, n):
        hand = list(combination)
        rank = evaluator.evaluate([], hand)

        if rank < best_rank:
            best_rank = rank
            best_hand = hand

    return best_hand

def format_hand(hand):
    sorted_hand = sorted(hand, key=lambda card: card)
    return " ".join([Card.int_to_pretty_str(card) for card in sorted_hand])

def format_hand_unsorted(hand):
    return " ".join([Card.int_to_pretty_str(card) for card in hand])

def find_min_sum(cards):
    evaluator = Evaluator()
    back = sorted(itertools.combinations(cards, 5), key=lambda x: evaluator.evaluate([], list(x)))
    A = [evaluator.evaluate([], list(x)) for x in back]

    min_sum = float('inf')
    result = None

    for x in range(len(A)):
        remaining_cards = [card for card in cards if card not in back[x]]
        middle = sorted(itertools.combinations(remaining_cards, 5), key=lambda x: evaluator.evaluate([], list(x)))
        B = [evaluator.evaluate([], list(x)) for x in middle]

        y = 0
        while y < len(B) and B[y] <= A[x]:
            y += 1
        if y == len(B):
            continue

        remaining_cards = [card for card in remaining_cards if card not in middle[y]]
        front = sorted(itertools.combinations(remaining_cards, 3), key=lambda x: evaluator.evaluate([Card.new('2c'), Card.new('2d')], list(x)))
        C = [evaluator.evaluate([Card.new('2c'), Card.new('2d')], list(x)) for x in front]
        z = 0
        while z < len(C) and C[z] <= B[y]:
            z += 1
        if z == len(C):
            continue

        current_sum = A[x] + B[y] + C[z]
        if current_sum < min_sum:
            min_sum = current_sum
            result = (list(back[x]), list(middle[y]), list(front[z]))

    return result, min_sum

@app.route("/", methods=["GET"])
def index():
    card_input = request.args.get('cards', default='', type=str)
    if not card_input:
        return jsonify({"error": "Please provide a string of 13 cards."}), 400

    cards = parse_cards(card_input)
    if isinstance(cards, str):  # If there's an error message
        return jsonify({"error": cards}), 400

    result = {
        "greedy": [],
        "minimax": []
    }

    greedy = cards
    for hand_size in [5, 5]:
        best_hand = make_hand(greedy, hand_size)
        result["greedy"].append(format_hand(best_hand))
        greedy = [card for card in greedy if card not in best_hand]

    result["greedy"].append(format_hand(greedy))

    minimax_hands, minimax_score = find_min_sum(cards)
    for hand in minimax_hands:
        result["minimax"].append(format_hand(hand))

    result["minimax_score"] = minimax_score

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
