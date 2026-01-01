import Foundation

class GameModel: ObservableObject {
    @Published var board: [[Int]] = Array(repeating: Array(repeating: 0, count: 10), count: 10)
    @Published var score: Int = 0
    @Published var gameOver: Bool = false
    
    init() {
        startNewGame()
    }
    
    func startNewGame() {
        // Initialize board with random values
        board = board.map { row in
            row.map { _ in Int.random(in: 1...9) }
        }
        score = 0
        gameOver = false
    }
    
    func handleCellTap(row: Int, column: Int) {
        guard isValidMove(row: row, column: column) else { return }
        
        let selectedNumber = board[row][column]
        score += selectedNumber
        
        // Update surrounding cells
        for i in max(0, row-1)...min(9, row+1) {
            for j in max(0, column-1)...min(9, column+1) {
                if i == row && j == column {
                    board[i][j] = 0
                } else {
                    board[i][j] = (board[i][j] + selectedNumber) % 10
                    if board[i][j] == 0 {
                        board[i][j] = 1
                    }
                }
            }
        }
        
        checkGameOver()
    }
    
    private func isValidMove(row: Int, column: Int) -> Bool {
        return board[row][column] != 0
    }
    
    private func checkGameOver() {
        // Game over if no more valid moves
        gameOver = !board.contains { row in
            row.contains { $0 != 0 }
        }
    }
}
