import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { X, Search } from "lucide-react"

interface CategorySelectorProps {
  onCategoriesChange: (categories: string[]) => void
}

const popularCategories = [
  "Bars",
  "Nightlife",
  "Thai",
  "Mexican",
  "Italian",
  "American (New)",
  "American (Traditional)",
  "Chinese",
  "Japanese",
  "Indian",
  "French",
  "Mediterranean",
  "Pizza",
  "Cafes",
  "Fast Food",
  "Breakfast & Brunch",
  "Seafood",
  "Steakhouses",
  "Vegetarian",
  "Vegan",
  "Restaurants",
  "Coffee & Tea",
  "Bakeries",
  "Sandwiches",
  "Burgers",
  "Sushi Bars",
  "Cocktail Bars",
  "Wine Bars",
  "Beer Bar",
  "Breweries",
  "Pubs"
];

export default function CategorySelector({ onCategoriesChange }: CategorySelectorProps) {
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")

  const filteredCategories = popularCategories.filter(
    (category) => category.toLowerCase().includes(searchTerm.toLowerCase()) && !selectedCategories.includes(category),
  )

  const handleCategoryAdd = (category: string) => {
    const newCategories = [...selectedCategories, category]
    setSelectedCategories(newCategories)
    onCategoriesChange(newCategories)
    setSearchTerm("")
  }

  const handleCategoryRemove = (category: string) => {
    const newCategories = selectedCategories.filter((c) => c !== category)
    setSelectedCategories(newCategories)
    onCategoriesChange(newCategories)
  }

  const handleCustomCategory = () => {
    if (searchTerm.trim() && !selectedCategories.includes(searchTerm.trim())) {
      handleCategoryAdd(searchTerm.trim())
    }
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Input
          placeholder="Search or enter a category..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleCustomCategory()}
          className="pr-10"
        />
        <Button size="icon" variant="ghost" className="absolute right-1 top-1 h-8 w-8" onClick={handleCustomCategory}>
          <Search className="w-4 h-4" />
        </Button>
      </div>

      {selectedCategories.length > 0 && (
        <div>
          <Label className="text-sm font-medium mb-2 block">Chosen categories:</Label>
          <div className="flex flex-wrap gap-2">
            {selectedCategories.map((category) => (
              <Badge key={category} variant="default" className="flex items-center gap-1">
                {category}
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-4 w-4 p-0 hover:bg-transparent"
                  onClick={() => handleCategoryRemove(category)}
                >
                  <X className="w-3 h-3" />
                </Button>
              </Badge>
            ))}
          </div>
        </div>
      )}

      {filteredCategories.length > 0 && (
        <div>
          <Label className="text-sm font-medium mb-2 block">
            {searchTerm ? "Search results:" : "Popular categories:"}
          </Label>
          <div className="flex flex-wrap gap-2">
            {filteredCategories.slice(0, 10).map((category) => (
              <Badge
                key={category}
                variant="outline"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                onClick={() => handleCategoryAdd(category)}
              >
                {category}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
