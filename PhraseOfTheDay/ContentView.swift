//
//  ContentView.swift
//  PhraseOfTheDay
//
//  Created by Amelia Mounts on 9/20/24.
//

import SwiftUI

struct FetchedPhrase: Codable {
    let phrase: String
    let description: String
    let example: String
}


struct ContentView: View {
    @State private var phrase: String = "Loading..."
    @State private var description: String = ""
    @State private var example: String = ""

    var body: some View {
        VStack {
            Text(phrase).font(.largeTitle).bold().multilineTextAlignment(.center).foregroundColor(Color("CustomPhraseColor"))
            Text(description).font(.headline).multilineTextAlignment(.center)
                .padding().foregroundColor(Color("CustomDescriptionColor"))
            Text(example).font(.body).multilineTextAlignment(.center).foregroundColor(Color("CustomDescriptionColor"))
        }
        .onAppear {
            fetchPhrase()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color("CustomBackgroundColor"))
    }

    // Function to fetch phrase from backend
    func fetchPhrase() {
        guard let url = URL(string: "http://127.0.0.1:5000/todaysPhrase") else {
            self.phrase = "Invalid URL"
            return
        }
        
        var request = URLRequest(url: url)
        let currDate = getCurrentDateString()
        
        request.httpMethod = "GET"
        request.setValue(currDate, forHTTPHeaderField: "Date")

        let task = URLSession.shared.dataTask(with: request) { data, response, error in
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

//            if let fetchedPhrase = String(data: data, encoding: .utf8) {
//                DispatchQueue.main.async {
//                    self.phrase = fetchedPhrase
//                }
            do {
                let decoder = JSONDecoder()
                let fetchedPhrase = try decoder.decode(FetchedPhrase.self, from: data)
                
                DispatchQueue.main.async {
                    // Update the UI with the parsed data
                    self.phrase = fetchedPhrase.phrase
                    self.description = fetchedPhrase.description
                    self.example = fetchedPhrase.example
                }
            } catch {
                print("Failed to decode JSON: \(error.localizedDescription)")
            }
        }

        task.resume()
    }
    
    func getCurrentDateString() -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd" // Customize format if needed
        return dateFormatter.string(from: Date())
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
