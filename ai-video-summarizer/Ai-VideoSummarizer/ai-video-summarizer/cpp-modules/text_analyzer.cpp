// text_analyzer.cpp - C++ module for fast text processing
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <cmath>

class TextAnalyzer {
private:
    std::unordered_map<std::string, int> wordFrequencies;
    std::vector<std::string> keywords;
    
public:
    TextAnalyzer() = default;
    
    // Extract keywords from text
    std::vector<std::string> extractKeywords(const std::string& text, int maxKeywords = 10) {
        wordFrequencies.clear();
        keywords.clear();
        
        // Simple tokenization
        std::string currentWord;
        for (char c : text) {
            if (std::isalpha(c) || c == '-') {
                currentWord += std::tolower(c);
            } else if (!currentWord.empty()) {
                if (currentWord.length() > 3) { // Ignore short words
                    wordFrequencies[currentWord]++;
                }
                currentWord.clear();
            }
        }
        
        // Get most frequent words
        std::vector<std::pair<std::string, int>> sortedWords;
        for (const auto& pair : wordFrequencies) {
            sortedWords.push_back(pair);
        }
        
        std::sort(sortedWords.begin(), sortedWords.end(),
                  [](const auto& a, const auto& b) {
                      return a.second > b.second;
                  });
        
        for (int i = 0; i < std::min(maxKeywords, (int)sortedWords.size()); i++) {
            keywords.push_back(sortedWords[i].first);
        }
        
        return keywords;
    }
    
    // Calculate text similarity (cosine similarity)
    double calculateSimilarity(const std::string& text1, const std::string& text2) {
        auto vec1 = createVector(text1);
        auto vec2 = createVector(text2);
        
        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;
        
        for (const auto& pair : vec1) {
            const std::string& word = pair.first;
            double freq1 = pair.second;
            
            norm1 += freq1 * freq1;
            
            if (vec2.count(word) > 0) {
                dotProduct += freq1 * vec2[word];
            }
        }
        
        for (const auto& pair : vec2) {
            norm2 += pair.second * pair.second;
        }
        
        if (norm1 == 0 || norm2 == 0) {
            return 0.0;
        }
        
        return dotProduct / (std::sqrt(norm1) * std::sqrt(norm2));
    }
    
private:
    std::unordered_map<std::string, double> createVector(const std::string& text) {
        std::unordered_map<std::string, int> localFreq;
        std::string currentWord;
        
        // Count word frequencies
        for (char c : text) {
            if (std::isalpha(c) || c == '-') {
                currentWord += std::tolower(c);
            } else if (!currentWord.empty()) {
                if (currentWord.length() > 3) {
                    localFreq[currentWord]++;
                }
                currentWord.clear();
            }
        }
        
        // Convert to TF (term frequency)
        std::unordered_map<std::string, double> vector;
        int totalWords = 0;
        
        for (const auto& pair : localFreq) {
            totalWords += pair.second;
        }
        
        if (totalWords > 0) {
            for (const auto& pair : localFreq) {
                vector[pair.first] = (double)pair.second / totalWords;
            }
        }
        
        return vector;
    }
};

// Main function for testing
int main() {
    TextAnalyzer analyzer;
    
    std::string sampleText = "Machine learning is a subset of artificial intelligence. "
                             "Machine learning algorithms build models based on sample data. "
                             "These models are used for making predictions or decisions.";
    
    auto keywords = analyzer.extractKeywords(sampleText);
    
    std::cout << "Extracted Keywords:" << std::endl;
    for (const auto& keyword : keywords) {
        std::cout << "- " << keyword << std::endl;
    }
    
    return 0;
}