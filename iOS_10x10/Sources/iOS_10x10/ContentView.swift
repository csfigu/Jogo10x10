import SwiftUI

struct ContentView: View {
    @StateObject private var gameModel = GameModel()
    
    var body: some View {
        VStack(spacing: 20) {
            Text("10x10 Game")
                .font(.largeTitle)
                .padding()
            
            // Game Board
            VStack(spacing: 2) {
                ForEach(0..<10, id: \.self) { row in
                    HStack(spacing: 2) {
                        ForEach(0..<10, id: \.self) { col in
                            Button(action: {
                                handleCellTap(row: row, column: col)
                            }) {
                                Text("\(gameModel.board[row][col])")
                                    .frame(width: 30, height: 30)
                                    .background(Color.blue)
                                    .foregroundColor(.white)
                                    .cornerRadius(4)
                            }
                        }
                    }
                }
            }
            
            // Score Display
            Text("Score: \(gameModel.score)")
                .font(.title)
            
            Spacer()
            
            if gameModel.gameOver {
                VStack {
                    Text("Game Over!")
                        .font(.title)
                        .padding()
                    Button(action: {
                        gameModel.startNewGame()
                    }) {
                        Text("Play Again")
                            .font(.title2)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                }
                .transition(.scale)
            }
        }
        .padding()
        .animation(.easeInOut, value: gameModel.gameOver)
    }
    
    private func handleCellTap(row: Int, column: Int) {
        gameModel.handleCellTap(row: row, column: column)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
