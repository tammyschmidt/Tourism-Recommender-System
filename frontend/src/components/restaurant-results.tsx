import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, MapPin, Clock, Phone, ExternalLink } from "lucide-react"

interface SearchCriteria {
  location: string
  cuisines: string[]
  setting: string
  preferences: {
    price: number[]
    distance: number[]
    rating: number[]
    waitTime: number[]
  }
  selectedUser: string
}

interface RestaurantResultsProps {
  searchCriteria: SearchCriteria
}

const sampleRestaurants = [
  {
    id: 1,
    name: "Bella Vista",
    cuisine: "Italian",
    rating: 4.5,
    priceLevel: 2,
    distance: "0.8 km",
    waitTime: "15-20 min",
    address: "Musterstraße 123, Berlin",
    phone: "+49 30 12345678",
    image: "/placeholder.svg?height=200&width=300",
    description: "Authentic Italian cuisine in a cozy atmosphere.",
    tags: ["Romantic", "Terrace", "Wine Bar"],
  },
  {
    id: 2,
    name: "Dragon Palace",
    cuisine: "Asian",
    rating: 4.3,
    priceLevel: 2,
    distance: "1.2 km",
    waitTime: "10-15 min",
    address: "Beispielweg 456, Berlin",
    phone: "+49 30 87654321",
    image: "/placeholder.svg?height=200&width=300",
    description: "Modern Asian fusion cuisine with fresh ingredients.",
    tags: ["Modern", "Sushi", "Vegetarian"],
  },
  {
    id: 3,
    name: "Gasthaus zum Hirsch",
    cuisine: "German",
    rating: 4.7,
    priceLevel: 3,
    distance: "2.1 km",
    waitTime: "25-30 min",
    address: "Traditionsgasse 789, Berlin",
    phone: "+49 30 11223344",
    image: "/placeholder.svg?height=200&width=300",
    description: "Traditional German cuisine in a historic ambiance.",
    tags: ["Traditional", "Beer Garden", "Family-Friendly"],
  },
]

export default function RestaurantResults({ searchCriteria }: RestaurantResultsProps) {
  const getPriceSymbol = (level: number) => {
    return (
      "€".repeat(level) +
      "€"
        .repeat(Math.max(0, 3 - level))
        .split("")
        .map((char, i) =>
          i < level ? (
            char
          ) : (
            <span key={i} className="opacity-30">
              {char}
            </span>
          ),
        )
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Restaurants Found</h2>
        <p className="text-gray-600">
          {sampleRestaurants.length} restaurants found
          {searchCriteria.location && ` in ${searchCriteria.location}`}
          {searchCriteria.selectedUser && ` for ${searchCriteria.selectedUser}`}
        </p>
      </div>

      <div className="grid gap-6">
        {sampleRestaurants.map((restaurant) => (
          <Card key={restaurant.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="md:flex">
              <div className="md:w-1/3">
                <img
                  src={restaurant.image || "/placeholder.svg"}
                  alt={restaurant.name}
                  className="w-full h-48 md:h-full object-cover"
                />
              </div>
              <div className="md:w-2/3">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl">{restaurant.name}</CardTitle>
                      <CardDescription className="flex items-center gap-4 mt-1">
                        <Badge variant="outline">{restaurant.cuisine}</Badge>
                        <div className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-medium">{restaurant.rating}</span>
                        </div>
                        <div className="flex items-center">{getPriceSymbol(restaurant.priceLevel)}</div>
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4">{restaurant.description}</p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{restaurant.distance}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span>{restaurant.waitTime}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span>{restaurant.address}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <span>{restaurant.phone}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {restaurant.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <Button className="flex-1">
                      <Phone className="w-4 h-4 mr-2" />
                      Call
                    </Button>
                    <Button variant="outline" className="flex-1">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Details
                    </Button>
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}