//
//  ContentView.swift
//  PhraseOfTheDay
//
//  Created by Amelia Mounts on 9/20/24.
//

import SwiftUI

struct ContentView: View {
    @State private var phrase: String = "Loading..."

    var body: some View {
        VStack {
            Text(phrase)
                .font(.largeTitle)
                .multilineTextAlignment(.center)
                .padding()

            //Spacer()
        }
        .onAppear {
            fetchPhrase()
        }
    }

    // Function to fetch phrase from backend
    func fetchPhrase() {
        guard let url = URL(string: "http://127.0.0.1:5000/todaysPhrase") else {
            self.phrase = "Invalid URL"
            return
        }

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    self.phrase = "Error: \(error.localizedDescription)"
                }
                return
            }

            guard let data = data else {
                DispatchQueue.main.async {
                    self.phrase = "No data received"
                }
                return
            }

            if let fetchedPhrase = String(data: data, encoding: .utf8) {
                DispatchQueue.main.async {
                    self.phrase = fetchedPhrase
                }
            } else {
                DispatchQueue.main.async {
                    self.phrase = "Failed to decode response"
                }
            }
        }

        task.resume()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
