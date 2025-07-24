'use client'

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Star, MapPin, Phone, ExternalLink, ArrowLeft, Utensils, Wifi, Car, CreditCard } from "lucide-react"
import { type Restaurant } from "@/services/api"

export default function RestaurantDetail() {
  const params = useParams()
  const navigate = useNavigate()
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get restaurant data from localStorage (passed from the list)
    const restaurantData = localStorage.getItem(`restaurant_${params.id}`)
    if (restaurantData) {
      setRestaurant(JSON.parse(restaurantData))
    }
    setLoading(false)
  }, [params.id])

  const getPriceSymbol = (level: number | null) => {
    if (level === null || level < 1) return null;
    return (
      <>
        {"€".repeat(level)}
        <span className="opacity-30">{"€".repeat(Math.max(0, 4 - level))}</span>
      </>
    )
  }

  const getAttributeIcon = (attribute: string) => {
    const attr = attribute.toLowerCase()
    if (attr.includes('wifi') || attr.includes('internet')) return <Wifi className="w-4 h-4" />
    if (attr.includes('parking')) return <Car className="w-4 h-4" />
    if (attr.includes('credit') || attr.includes('card')) return <CreditCard className="w-4 h-4" />
    return <Utensils className="w-4 h-4" />
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    )
  }

  if (!restaurant) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Zurück zur Suche
        </Button>
        <Card>
          <CardContent className="p-8 text-center">
            <h2 className="text-xl font-semibold mb-2">Restaurant nicht gefunden</h2>
            <p className="text-muted-foreground">Das angeforderte Restaurant konnte nicht geladen werden.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Button 
        variant="ghost" 
        onClick={() => navigate('/')}
        className="mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Zurück zur Suche
      </Button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Restaurant Info */}
        <div className="lg:col-span-2">
          <Card>
            <div className="w-full h-64 bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center rounded-t-lg">
              <Utensils className="w-24 h-24 text-orange-400" />
            </div>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-3xl mb-2">{restaurant.name || "Unnamed Restaurant"}</CardTitle>
                  <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-2 text-lg">
                    {restaurant.categories && restaurant.categories.length > 0 && (
                      <Badge variant="outline" className="text-sm">{restaurant.categories[0]}</Badge>
                    )}
                    {restaurant.rating !== null && (
                      <div className="flex items-center gap-1">
                        <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                        <span className="font-medium text-lg">{restaurant.rating.toFixed(1)}</span>
                      </div>
                    )}
                    {restaurant.price_level !== null && (
                      <div className="flex items-center font-semibold text-muted-foreground text-lg">
                        {getPriceSymbol(restaurant.price_level)}
                      </div>
                    )}
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {restaurant.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-2">Beschreibung</h3>
                  <p className="text-muted-foreground leading-relaxed">{restaurant.description}</p>
                </div>
              )}

              {restaurant.categories && restaurant.categories.length > 1 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">Kategorien</h3>
                  <div className="flex flex-wrap gap-2">
                    {restaurant.categories.map((category: string, index: number) => (
                      <Badge key={index} variant="secondary">
                        {category}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {restaurant.attributes && restaurant.attributes.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-3">Ausstattung & Services</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {restaurant.attributes.map((attr: string, index: number) => (
                      <div key={index} className="flex items-center gap-2 p-2 bg-muted/50 rounded-lg">
                        {getAttributeIcon(attr)}
                        <span className="text-sm">{attr}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Sidebar with Contact & Actions */}
        <div className="lg:col-span-1">
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle className="text-xl">Kontakt & Informationen</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {restaurant.address && (
                <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                  <MapPin className="w-5 h-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium text-sm">Adresse</p>
                    <p className="text-sm text-muted-foreground">{restaurant.address}</p>
                  </div>
                </div>
              )}

              {restaurant.phone && (
                <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                  <Phone className="w-5 h-5 text-muted-foreground mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">Telefon</p>
                    <p className="text-sm text-muted-foreground">{restaurant.phone}</p>
                  </div>
                </div>
              )}

              <div className="space-y-2 pt-4">
                {restaurant.phone && (
                  <Button 
                    className="w-full" 
                    onClick={() => window.open(`tel:${restaurant.phone}`)}
                  >
                    <Phone className="w-4 h-4 mr-2" />
                    Anrufen
                  </Button>
                )}
                {restaurant.address && (
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(restaurant.address || '')}`, '_blank')}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    In Google Maps öffnen
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
