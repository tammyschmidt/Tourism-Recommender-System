import { useState, useEffect, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Star, MapPin, Phone, ExternalLink, Loader2, AlertCircle, Utensils } from "lucide-react"
import { 
  type Restaurant,
  type RecommendationRequest,
  getPopularRestaurants,
  getRecommendations,
  geocodeLocation
} from "@/services/api"

interface SearchCriteria {
  location: string
  categories: string[]
  attributes: string[]
  preferences: {
    price: number[]
    distance: number[]
    rating: number[]
    waitTime: number[]
  }
  requestedDay: string | null
  requestedTime: string | null
}

interface RestaurantResultsProps {
  searchCriteria: SearchCriteria
}

export default function RestaurantResults({ searchCriteria }: RestaurantResultsProps) {
  const navigate = useNavigate()
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [resultsCount, setResultsCount] = useState<number>(20)

  const getPriceSymbol = (level: number | null) => {
    if (level === null || level < 1) return null;
    return (
      <>
        {"€".repeat(level)}
        <span className="opacity-30">{"€".repeat(Math.max(0, 4 - level))}</span>
      </>
    )
  }



  const fetchRestaurants = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    console.log('DEBUG: searchCriteria:', JSON.stringify(searchCriteria, null, 2))
    
    try {
      let results: Restaurant[] = []
      
      if (searchCriteria.location || searchCriteria.categories.length > 0 || searchCriteria.attributes.length > 0 || searchCriteria.requestedDay || searchCriteria.requestedTime) {
        const request: RecommendationRequest = { top_n: resultsCount }

        if (searchCriteria.location) {
          const parts = searchCriteria.location.split(',');
          const cityName = parts[parts.length - 1]?.trim() || undefined;

          try {
            const coordinates = await geocodeLocation(searchCriteria.location)
            request.latitude = coordinates.latitude
            request.longitude = coordinates.longitude
            request.maxDistance = 5000
          } catch (geocodeError) {
            console.warn("Geocoding failed, will proceed with city search only:", geocodeError)
          }

          if (cityName) {
            request.city = cityName;
          }
        }
        
        if (searchCriteria.categories.length > 0) {
          request.inputCategories = searchCriteria.categories
        }

        if (searchCriteria.attributes.length > 0) {
          request.requiredAttributes = searchCriteria.attributes
          console.log('DEBUG: Sending attributes to API:', searchCriteria.attributes)
        } else {
          console.log('DEBUG: No attributes selected, searchCriteria.attributes:', searchCriteria.attributes)
          // TEMPORARY FIX: Force attribute filtering since frontend attribute selection is broken
          if (searchCriteria.location && searchCriteria.location.toLowerCase().includes('nashville')) {
            // Force Free WiFi filtering as a test
            request.requiredAttributes = ['Free WiFi']
            console.log('DEBUG: FORCED Free WiFi attribute for testing:', request.requiredAttributes)
          }
        }
        
        if (searchCriteria.requestedDay) {
          request.requestedDay = searchCriteria.requestedDay
        }
        
        if (searchCriteria.requestedTime) {
          request.requestedTime = searchCriteria.requestedTime
        }


        
        const prefs = searchCriteria.preferences;
        request.weights = [
          1.0,
          prefs.price[0] / 100,
          prefs.rating[0] / 100,
          prefs.distance[0] / 100,
        ];

        console.log('DEBUG: Complete API request:', JSON.stringify(request, null, 2))
        results = await getRecommendations(request)
      } else {
        results = await getPopularRestaurants()
      }
      
      setRestaurants(results)
    } catch (err) {
      console.error('Error fetching restaurants:', err)
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.'
      setError(`Failed to fetch restaurants. ${errorMessage}`)
    } finally {
      setLoading(false)
    }
  }, [searchCriteria, resultsCount])

  useEffect(() => {
    fetchRestaurants()
  }, [fetchRestaurants])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin mr-2" />
        <span className="text-lg">Finding restaurants...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center p-4 border border-red-200 bg-red-50 rounded-lg">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 mb-4 font-semibold">Could not load results</p>
          <p className="text-sm text-red-500 mb-4">{error}</p>
          <Button 
            variant="outline" 
            onClick={fetchRestaurants}
          >
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Your Recommendations</h2>
        <p className="text-muted-foreground">
          {restaurants.length} results found
        </p>
      </div>

      <div className="flex justify-center">
        <div className="flex items-center gap-3">
          <Label htmlFor="results-count" className="text-sm font-medium">
            Show results:
          </Label>
          <Select
            value={resultsCount.toString()}
            onValueChange={(value) => setResultsCount(parseInt(value))}
          >
            <SelectTrigger className="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="30">30</SelectItem>
              <SelectItem value="50">50</SelectItem>
              <SelectItem value="100">100</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {restaurants.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground text-lg mb-4">No restaurants found matching your criteria.</p>
          <p className="text-sm text-muted-foreground">Try adjusting your filters.</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {restaurants.map((restaurant) => (
          <Card key={restaurant.id} className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer" onClick={() => {
            // Store restaurant data in localStorage for the detail page
            localStorage.setItem(`restaurant_${restaurant.id}`, JSON.stringify(restaurant));
            navigate(`/restaurant/${restaurant.id}`);
          }}>
            <div className="md:flex">
              <div className="md:w-1/3">
                <div className="w-full h-48 md:h-full bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center">
                  <Utensils className="w-16 h-16 text-orange-400" />
                </div>
              </div>
              <div className="md:w-2/3 p-4">
                <CardHeader className="p-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-xl">{restaurant.name || "Unnamed Restaurant"}</CardTitle>
                      <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1">
                        {restaurant.categories && restaurant.categories.length > 0 && (
                          <Badge variant="outline">{restaurant.categories[0]}</Badge>
                        )}
                        {restaurant.rating !== null && (
                          <div className="flex items-center gap-1">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-medium">{restaurant.rating.toFixed(1)}</span>
                          </div>
                        )}
                        {restaurant.price_level !== null && (
                           <div className="flex items-center font-semibold text-muted-foreground">{getPriceSymbol(restaurant.price_level)}</div>
                        )}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-2">
                  {restaurant.description && (
                    <p className="text-muted-foreground mb-4 text-sm">{restaurant.description}</p>
                  )}

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                    {restaurant.address && (
                      <div className="flex items-start gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                        <span>{restaurant.address}</span>
                      </div>
                    )}
                    {restaurant.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="w-4 h-4 text-muted-foreground" />
                        <span>{restaurant.phone}</span>
                      </div>
                    )}
                  </div>

                  {restaurant.attributes && restaurant.attributes.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {restaurant.attributes.map((attr: string, index: number) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {attr}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-2 mt-4">
                    <Button 
                      className="flex-1" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        // Store restaurant data in localStorage for the detail page
                        localStorage.setItem(`restaurant_${restaurant.id}`, JSON.stringify(restaurant));
                        navigate(`/restaurant/${restaurant.id}`);
                      }}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Mehr Details
                    </Button>
                    {restaurant.phone && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={(e) => {
                          e.stopPropagation();
                          window.open(`tel:${restaurant.phone}`);
                        }}
                      >
                        <Phone className="w-4 h-4 mr-2" />
                        Anrufen
                      </Button>
                    )}
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
          ))}
        </div>
      )}
    </div>
  )
}