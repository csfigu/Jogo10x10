import Foundation
import SwiftUI

class NumberPuzzleGameLogic: ObservableObject {
    @Published var size: Int = 10
    @Published var board: [[Int]] = []
    @Published var currentNumber: Int = 1
    @Published var gameOver: Bool = false
    @Published var currentPosition: (Int, Int)? = nil
    @Published var moves: [(Int, Int)] = []
    @Published var startTime: Date? = nil
    @Published var elapsedTime: Int = 0
    @Published var topScores: [String: [(String, Int, Int)]] = ["10x10": [], "5x5": []]
    @Published var currentTheme: String = "white"
    @Published var themes: [String: [String: Any]] = [
        "white": [
            "bg": Color.white,
            "fg": Color.black,
            "button_bg": Color(.systemGray6),
            "button_fg": Color.black,
            "button_active_bg": Color(.systemGray4)
        ],
        "dark": [
            "bg": Color(.systemGray6),
            "fg": Color.white,
            "button_bg": Color(.systemGray4),
            "button_fg": Color.white,
            "button_active_bg": Color(.systemGray2)
        ]
    ]

    let scoresFile: String = "scores.json"

    init() {
        loadScores()
        createBoard()
    }

    func createBoard() {
        board = Array(repeating: Array(repeating: 0, count: size), count: size)
    }

    func setBoardSize(size: Int) {
        self.size = size
        createBoard()
        startNewGame()
    }

    func startNewGame() {
        createBoard()
        currentNumber = 1
        gameOver = false
        currentPosition = nil
        moves = []
        startTime = nil
        elapsedTime = 0
    }

    func isValidPosition(row: Int, col: Int) -> Bool {
        return row >= 0 && row < size && col >= 0 && col < size
    }

    func isValidMove(nextRow: Int, nextCol: Int) -> Bool {
        if !isValidPosition(row: nextRow, col: nextCol) {
            return false
        }
        if board[nextRow][nextCol] != 0 {
            return false
        }
        return true
    }

    func getPossibleMoves() -> [(Int, Int)] {
        guard let (row, col) = currentPosition else {
            return []
        }

        var possibleMoves: [(Int, Int)] = []

        // Straight moves
        let movesStraight = [(0, -3), (0, 3), (-3, 0), (3, 0)]
        for (dr, dc) in movesStraight {
            let nextRow = row + dr
            let nextCol = col + dc
            if isValidMove(nextRow: nextRow, nextCol: nextCol) {
                possibleMoves.append((nextRow, nextCol))
            }
        }

        // Diagonal moves
        let movesDiagonal = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for (dr, dc) in movesDiagonal {
            let nextRow = row + dr
            let nextCol = col + dc
            if isValidMove(nextRow: nextRow, nextCol: nextCol) {
                possibleMoves.append((nextRow, nextCol))
            }
        }

        return possibleMoves
    }

    func makeMove(row: Int, col: Int) {
        if gameOver {
            return
        }

        if currentNumber == 1 {
            startTime = Date()
            board[row][col] = currentNumber
            currentPosition = (row, col)
            moves.append((row, col))
            currentNumber += 1
            return
        }

        if !isValidMove(nextRow: row, nextCol: col) {
            return
        }

        let possibleMoves = getPossibleMoves()
        if !possibleMoves.contains(where: { $0.0 == row && $0.1 == col }) {
            return
        }

        board[row][col] = currentNumber
        currentPosition = (row, col)
        moves.append((row, col))
        currentNumber += 1

        if getPossibleMoves().isEmpty {
            endGame()
        }
    }

    func endGame() {
        gameOver = true
        elapsedTime = Int(Date().timeIntervalSince(startTime ?? Date()))
    }

    func loadScores() {
        // TODO: Implement loading scores from JSON file
        // topScores = ["10x10": [], "5x5": []] // Placeholder
    }

    func saveScores() {
        // TODO: Implement saving scores to JSON file
    }

    func checkHighScore(score: Int, elapsedTime: Int) {
        // TODO: Implement high score checking and saving
    }

    func updateScoreList() {
        // TODO: Implement score list updating
    }

    func getColor(number: Int) -> Color {
        let max_value = size * size
        let progress = Double(number - 1) / Double(max_value - 1)
        
        // Color transition: blue (240°) to red (0°)
        let hue = 240.0 - (progress * 240.0)
        let saturation = 0.7 + (progress * 0.3)  // 70-100%
        let value = 0.8 + (progress * 0.2)       # 80-100%
        
        // Convert HSV to RGB
        let h = hue / 360
        let i = floor(h * 6)
        let f = h * 6 - i
        let p = value * (1 - saturation)
        let q = value * (1 - f * saturation)
        let t = value * (1 - (1 - f) * saturation)

        let intI = Int(i.truncatingRemainder(dividingBy: 6))
        var r: Double = 0.0
        var g: Double = 0.0
        var b: Double = 0.0

        if intI == 0 { r = value; g = t; b = p }
        else if intI == 1 { r = q; g = value; b = p }
        else if intI == 2 { r = p; g = value; b = t }
        else if intI == 3 { r = p; g = q; b = value }
        else if intI == 4 { r = t; g = p; b = value }
        else { r = value; g = p; b = q }

        return Color(red: r, green: g, blue: b)
    }
}
